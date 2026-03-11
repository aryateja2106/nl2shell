"""
NL2Shell v2 Dataset Builder
============================
Combines:
  1. GWHed/nl2bash          (~8,090 rows)  — columns: nl, bash
  2. AnishJoshi/nl2bash-custom (~19,658 rows) — columns: nl_command, bash_code
  3. 40 macOS synthetic pairs

Deduplicates by bash command, formats as ChatML, and pushes to
HuggingFace as AryaYT/nl2shell-training.
"""

import os

import pandas as pd
from datasets import Dataset, load_dataset

HF_TOKEN = os.environ.get("HF_TOKEN", "")
OUTPUT_REPO = "AryaYT/nl2shell-training"

SYSTEM_PROMPT = (
    "You are an expert shell programmer. Given a natural language request, "
    "output ONLY the corresponding shell command. No explanations."
)

# ── macOS Synthetic Pairs (copied from prepare.py) ─────────────────────────
MACOS_PAIRS = [
    ("list all installed homebrew packages", "brew list"),
    ("update homebrew and upgrade all packages", "brew update && brew upgrade"),
    ("show disk usage of current directory", "du -sh ."),
    ("find all Python files modified in the last 24 hours", "find . -name '*.py' -mtime -1"),
    ("show all running Docker containers", "docker ps"),
    ("kill the process using port 3000", "lsof -ti:3000 | xargs kill -9"),
    ("create a new git branch called feature-auth", "git checkout -b feature-auth"),
    ("show git log as one-line summaries", "git log --oneline -20"),
    ("compress the src directory into a tar.gz", "tar -czf src.tar.gz src/"),
    ("show system memory usage", "vm_stat | head -10"),
    ("list all open network connections", "lsof -i -P -n | head -20"),
    ("recursively find files larger than 100MB", "find / -size +100M -type f 2>/dev/null"),
    ("show the last 50 lines of the system log", "tail -50 /var/log/system.log"),
    (
        "restart the DNS cache on macOS",
        "sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder",
    ),
    ("show all environment variables containing PATH", "env | grep PATH"),
    ("count lines of code in all TypeScript files", "find . -name '*.ts' | xargs wc -l"),
    ("check if port 8080 is in use", "lsof -i :8080"),
    ("show the top 10 largest files in current directory", "ls -lhS | head -10"),
    ("create an SSH tunnel from local 8080 to remote 80", "ssh -L 8080:localhost:80 user@host"),
    ("watch a directory for file changes", "fswatch -r . | head -20"),
    ("install a package globally with npm", "npm install -g package-name"),
    ("run a Python HTTP server on port 8000", "python3 -m http.server 8000"),
    ("show all cron jobs for current user", "crontab -l"),
    (
        "check SSL certificate expiry of a domain",
        "echo | openssl s_client -connect example.com:443 2>/dev/null | openssl x509 -noout -dates",
    ),
    ("search for a string recursively in all files", "grep -r 'search_string' ."),
    ("show CPU and memory usage of all processes", "top -l 1 | head -20"),
    ("generate a random 32-character password", "openssl rand -base64 32"),
    ("download a file with curl and save it", "curl -LO https://example.com/file.tar.gz"),
    ("show the size of each subdirectory", "du -sh */ | sort -rh"),
    ("list all git branches sorted by last commit date", "git branch --sort=-committerdate"),
    ("set a file as executable", "chmod +x script.sh"),
    ("show the difference between two files", "diff file1.txt file2.txt"),
    (
        "find and delete all node_modules directories",
        "find . -name 'node_modules' -type d -prune -exec rm -rf {} +",
    ),
    ("show which process is using the most CPU", "ps aux --sort=-%cpu | head -5"),
    ("create a symbolic link", "ln -s /path/to/original /path/to/link"),
    ("watch the output of a command every 2 seconds", "watch -n 2 'command'"),
    ("show all listening TCP ports", "netstat -tlnp 2>/dev/null || ss -tlnp"),
    ("convert a video to mp4 using ffmpeg", "ffmpeg -i input.mov -c:v libx264 -c:a aac output.mp4"),
    ("show git stash list", "git stash list"),
    ("run a command in the background and disown it", "nohup command &>/dev/null & disown"),
]


def format_chatml(nl: str, cmd: str) -> str:
    """Format a single NL/CMD pair as ChatML."""
    return (
        f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n"
        f"<|im_start|>user\n{nl}<|im_end|>\n"
        f"<|im_start|>assistant\n{cmd}<|im_end|>"
    )


def load_gwhed() -> pd.DataFrame:
    """Load GWHed/nl2bash (columns: nl, bash)."""
    print("Loading GWHed/nl2bash...")
    ds = load_dataset("GWHed/nl2bash", split="train", token=HF_TOKEN)
    df = ds.to_pandas()[["nl", "bash"]].copy()  # type: ignore[union-attr]
    df = df.rename(columns={"nl": "nl", "bash": "bash"})
    df["source"] = "GWHed/nl2bash"
    print(f"  Loaded {len(df)} rows from GWHed/nl2bash")
    return df


def load_anish() -> pd.DataFrame:
    """Load AnishJoshi/nl2bash-custom (columns: nl_command, bash_code)."""
    print("Loading AnishJoshi/nl2bash-custom...")
    ds = load_dataset("AnishJoshi/nl2bash-custom", split="train", token=HF_TOKEN)
    df = ds.to_pandas()[["nl_command", "bash_code"]].copy()  # type: ignore[union-attr]
    df = df.rename(columns={"nl_command": "nl", "bash_code": "bash"})
    df["source"] = "AnishJoshi/nl2bash-custom"
    print(f"  Loaded {len(df)} rows from AnishJoshi/nl2bash-custom")
    return df


def load_macos() -> pd.DataFrame:
    """Build DataFrame from the 40 macOS synthetic pairs."""
    rows = [{"nl": nl, "bash": cmd, "source": "macos-synthetic"} for nl, cmd in MACOS_PAIRS]
    df = pd.DataFrame(rows)
    print(f"  Added {len(df)} macOS synthetic pairs")
    return df


def build_dataset() -> Dataset:
    # 1. Load all sources
    df_gwhed = load_gwhed()
    df_anish = load_anish()
    df_macos = load_macos()

    # 2. Concatenate
    df = pd.concat([df_gwhed, df_anish, df_macos], ignore_index=True)
    print(f"\nRaw combined rows: {len(df)}")

    # 3. Normalize — strip whitespace, drop empty
    df["nl"] = df["nl"].astype(str).str.strip()
    df["bash"] = df["bash"].astype(str).str.strip()
    df = df[(df["nl"] != "") & (df["bash"] != "") & (df["nl"] != "nan") & (df["bash"] != "nan")]
    print(f"After dropping empty rows: {len(df)}")

    # 4. Deduplicate by bash command (keep first occurrence — GWHed has priority)
    before_dedup = len(df)
    df = df.drop_duplicates(subset=["bash"], keep="first")
    print(f"After dedup by bash command: {len(df)} (removed {before_dedup - len(df)} duplicates)")

    # 5. Print statistics
    print("\n" + "=" * 50)
    print("DATASET STATISTICS")
    print("=" * 50)
    print(f"Total rows:        {len(df)}")
    print(f"Unique commands:   {df['bash'].nunique()}")
    print("\nSource breakdown:")
    for source, count in df["source"].value_counts().items():
        print(f"  {source}: {count}")
    print("=" * 50 + "\n")

    # 6. Format as ChatML
    df["text"] = df.apply(lambda row: format_chatml(row["nl"], row["bash"]), axis=1)

    # 7. Build HuggingFace Dataset with all four columns
    hf_dataset = Dataset.from_pandas(df[["text", "nl", "bash", "source"]].reset_index(drop=True))
    return hf_dataset


def main():
    print("NL2Shell v2 Dataset Builder")
    print("=" * 50)

    dataset = build_dataset()

    print(f"Pushing {len(dataset)} examples to HuggingFace: {OUTPUT_REPO}")
    dataset.push_to_hub(
        OUTPUT_REPO,
        token=HF_TOKEN,
        private=False,
    )
    print(f"\nDataset successfully pushed to: https://huggingface.co/datasets/{OUTPUT_REPO}")


if __name__ == "__main__":
    main()
