"""
NL2Shell v3 Dataset Builder
============================
Combines:
  1. v2 dataset (AryaYT/nl2shell-training) — 11,894 deduplicated pairs
  2. Expert-curated pairs from expert_pairs.py   — senior-engineer-level commands
  3. (Optional) LLM-rewritten naive pairs via Claude API  (--rewrite flag)

Deduplicates by bash command (expert pairs take priority on conflicts), formats
as ChatML, and optionally pushes to AryaYT/nl2shell-training-v3.

Usage
-----
# Build locally and push to HuggingFace:
    python build_v3_dataset.py --push

# Build and save to disk as parquet:
    python build_v3_dataset.py --local

# Build with LLM rewrites (costs money — uses Claude API):
    python build_v3_dataset.py --rewrite --push

# All flags at once:
    python build_v3_dataset.py --push --local --rewrite

Environment Variables
---------------------
HF_TOKEN           — HuggingFace write token (required for --push and loading private datasets)
ANTHROPIC_API_KEY  — Anthropic API key (required only when --rewrite is passed)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pandas as pd
from datasets import Dataset, load_dataset

# ── Constants ─────────────────────────────────────────────────────────────────

HF_TOKEN = os.environ.get("HF_TOKEN", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

V2_REPO = "AryaYT/nl2shell-training"
V3_REPO = "AryaYT/nl2shell-training-v3"
LOCAL_PARQUET = Path("data/v3-dataset.parquet")

SYSTEM_PROMPT = (
    "You are an expert shell programmer. Given a natural language request, "
    "output ONLY the corresponding shell command. No explanations."
)

# Number of naive v2 pairs to sample for LLM rewriting
REWRITE_SAMPLE_SIZE = 500

# Claude model used for rewrites — use a fast/cheap model since this is batch work
REWRITE_MODEL = "claude-3-5-haiku-20241022"

REWRITE_SYSTEM = (
    "You are a senior shell engineer with 15+ years of experience. "
    "You will be given a natural language description and a naive shell command. "
    "Rewrite the shell command the way a senior engineer would actually write it: "
    "use idiomatic flags, pipelines, proper quoting, error handling, and prefer "
    "efficient one-liners. If the naive command is already expert-quality, return "
    "it unchanged. Output ONLY the improved shell command — no explanation, no "
    "markdown fences, no commentary."
)


# ── ChatML Formatter ──────────────────────────────────────────────────────────


def format_chatml(nl: str, cmd: str) -> str:
    """Format a single NL/CMD pair as a ChatML conversation string."""
    return (
        f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n"
        f"<|im_start|>user\n{nl}<|im_end|>\n"
        f"<|im_start|>assistant\n{cmd}<|im_end|>"
    )


# ── Data Loaders ──────────────────────────────────────────────────────────────


def load_v2() -> pd.DataFrame:
    """Load the published v2 dataset from HuggingFace."""
    print(f"Loading v2 dataset from {V2_REPO}...")
    token = HF_TOKEN or None
    ds = load_dataset(V2_REPO, split="train", token=token)
    df = ds.to_pandas()[["nl", "bash", "source"]].copy()  # type: ignore[union-attr]
    df["nl"] = df["nl"].astype(str).str.strip()
    df["bash"] = df["bash"].astype(str).str.strip()
    print(f"  Loaded {len(df)} rows from v2")
    return df


def load_expert_pairs() -> pd.DataFrame:
    """Import EXPERT_PAIRS from expert_pairs.py and return a DataFrame."""
    try:
        # Allow running from any working directory
        sys.path.insert(0, str(Path(__file__).parent))
        from expert_pairs import EXPERT_PAIRS
    except ImportError:
        print(
            "  [WARNING] expert_pairs.py not found — skipping expert pairs.\n"
            "            Create expert_pairs.py with EXPERT_PAIRS = [(nl, cmd), ...] "
            "to include expert-curated data."
        )
        return pd.DataFrame(columns=["nl", "bash", "source"])

    rows = [
        {"nl": str(nl).strip(), "bash": str(cmd).strip(), "source": "expert-curated"}
        for nl, cmd in EXPERT_PAIRS
        if str(nl).strip() and str(cmd).strip()
    ]
    df = pd.DataFrame(rows)
    print(f"  Loaded {len(df)} expert-curated pairs from expert_pairs.py")
    return df


# ── LLM Rewrite (optional, expensive) ────────────────────────────────────────


def rewrite_naive_pairs(df_v2: pd.DataFrame) -> pd.DataFrame:
    """
    Sample REWRITE_SAMPLE_SIZE naive pairs from v2 and ask Claude to rewrite
    the shell commands as a senior engineer would.

    Returns a DataFrame of improved pairs with source="llm-rewrite".
    Only pairs where the rewrite differs from the original are included.
    """
    if not ANTHROPIC_API_KEY:
        print(
            "[ERROR] --rewrite requires ANTHROPIC_API_KEY to be set. "
            "Export the variable and try again."
        )
        sys.exit(1)

    try:
        import anthropic
    except ImportError:
        print(
            "[ERROR] --rewrite requires the `anthropic` package.\n"
            "        Install it with:  pip install anthropic"
        )
        sys.exit(1)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Sample from non-expert sources to find "naive" pairs
    naive_mask = df_v2["source"].isin(["GWHed/nl2bash", "AnishJoshi/nl2bash-custom"])
    naive_df = df_v2[naive_mask].sample(
        n=min(REWRITE_SAMPLE_SIZE, naive_mask.sum()), random_state=42
    )

    print(f"\nRewriting {len(naive_df)} naive pairs with Claude ({REWRITE_MODEL})...")
    print("  This will make one API call per pair — may take a few minutes.")

    rewritten_rows: list[dict[str, str]] = []
    improved_count = 0

    for i, row in enumerate(naive_df.itertuples(), start=1):
        if i % 50 == 0:
            print(f"  Progress: {i}/{len(naive_df)} ({improved_count} improved so far)")

        user_content = (
            f"Natural language: {row.nl}\n"
            f"Naive command: {row.bash}\n\n"
            "Write the improved shell command:"
        )

        try:
            message = client.messages.create(
                model=REWRITE_MODEL,
                max_tokens=256,
                system=REWRITE_SYSTEM,
                messages=[{"role": "user", "content": user_content}],
            )
            improved_cmd = message.content[0].text.strip()
        except Exception as exc:
            print(f"  [WARN] API error on row {i} ({row.nl[:40]!r}): {exc}")
            continue

        # Only include the pair if the rewrite is actually different
        if improved_cmd and improved_cmd != row.bash:
            rewritten_rows.append(
                {
                    "nl": row.nl,
                    "bash": improved_cmd,
                    "source": "llm-rewrite",
                }
            )
            improved_count += 1

    df_rewrites = pd.DataFrame(rewritten_rows)
    print(f"  LLM rewrites: {len(df_rewrites)} improved commands out of {len(naive_df)} sampled")
    return df_rewrites


# ── Core Build Logic ──────────────────────────────────────────────────────────


def build_dataset(rewrite: bool) -> Dataset:
    """
    Assemble the v3 dataset by merging v2, expert pairs, and (optionally)
    LLM rewrites. Expert pairs take priority over v2 on bash-command conflicts;
    LLM rewrites take lowest priority (added last, drop_duplicates keep=first).
    """
    # ── 1. Load sources ────────────────────────────────────────────────────────
    df_v2 = load_v2()
    df_expert = load_expert_pairs()

    frames: list[pd.DataFrame] = []

    # Expert pairs go first so they win deduplication
    if not df_expert.empty:
        frames.append(df_expert)

    frames.append(df_v2)

    # Optionally add LLM rewrites (lowest priority)
    if rewrite:
        df_rewrites = rewrite_naive_pairs(df_v2)
        if not df_rewrites.empty:
            frames.append(df_rewrites)

    # ── 2. Concatenate ─────────────────────────────────────────────────────────
    df = pd.concat(frames, ignore_index=True)
    print(f"\nRaw combined rows: {len(df)}")

    # ── 3. Normalize ───────────────────────────────────────────────────────────
    df["nl"] = df["nl"].astype(str).str.strip()
    df["bash"] = df["bash"].astype(str).str.strip()
    bad_mask = (df["nl"] == "") | (df["bash"] == "") | (df["nl"] == "nan") | (df["bash"] == "nan")
    df = df[~bad_mask].copy()
    print(f"After dropping empty/nan rows: {len(df)}")

    # ── 4. Deduplicate by bash command (expert first = keep="first") ────────────
    before_dedup = len(df)
    df = df.drop_duplicates(subset=["bash"], keep="first")
    removed = before_dedup - len(df)
    print(f"After dedup by bash command: {len(df)} (removed {removed} duplicates)")

    # ── 5. Print statistics ────────────────────────────────────────────────────
    print()
    print("=" * 55)
    print("DATASET STATISTICS — v3")
    print("=" * 55)
    print(f"{'Total rows:':<25} {len(df)}")
    print(f"{'Unique bash commands:':<25} {df['bash'].nunique()}")
    print()
    print("Source breakdown:")
    for source, count in df["source"].value_counts().items():
        pct = 100.0 * count / len(df)
        print(f"  {source:<38} {count:>6}  ({pct:.1f}%)")
    print("=" * 55)
    print()

    # ── 6. Format ChatML ───────────────────────────────────────────────────────
    df["text"] = df.apply(lambda row: format_chatml(row["nl"], row["bash"]), axis=1)

    # ── 7. Build HuggingFace Dataset ───────────────────────────────────────────
    hf_dataset = Dataset.from_pandas(df[["text", "nl", "bash", "source"]].reset_index(drop=True))
    return hf_dataset


# ── Entry Point ───────────────────────────────────────────────────────────────


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the NL2Shell v3 training dataset.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help=f"Push the dataset to HuggingFace as {V3_REPO}. Requires HF_TOKEN env var.",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help=f"Save the dataset locally as a parquet file at {LOCAL_PARQUET}.",
    )
    parser.add_argument(
        "--rewrite",
        action="store_true",
        help=(
            f"Sample {REWRITE_SAMPLE_SIZE} naive v2 pairs and rewrite them with Claude. "
            "Requires ANTHROPIC_API_KEY env var. WARNING: costs API credits."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("NL2Shell v3 Dataset Builder")
    print("=" * 55)

    if args.push and not HF_TOKEN:
        print("[ERROR] --push requires HF_TOKEN to be set as an environment variable.")
        sys.exit(1)

    dataset = build_dataset(rewrite=args.rewrite)

    # ── Local save ─────────────────────────────────────────────────────────────
    if args.local:
        LOCAL_PARQUET.parent.mkdir(parents=True, exist_ok=True)
        df_out = dataset.to_pandas()
        df_out.to_parquet(LOCAL_PARQUET, index=False)  # type: ignore[union-attr]
        print(f"Dataset saved locally to: {LOCAL_PARQUET.resolve()}")

    # ── HuggingFace push ───────────────────────────────────────────────────────
    if args.push:
        print(f"Pushing {len(dataset)} examples to HuggingFace: {V3_REPO}")
        dataset.push_to_hub(
            V3_REPO,
            token=HF_TOKEN,
            private=False,
        )
        print(f"Dataset successfully pushed to: https://huggingface.co/datasets/{V3_REPO}")

    if not args.push and not args.local:
        print(
            "Dataset built in memory. Pass --push to upload to HuggingFace "
            "or --local to save as parquet."
        )
        print(f"Total rows: {len(dataset)}")


if __name__ == "__main__":
    main()
