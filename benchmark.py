"""
NL2Shell Benchmark — Evaluate on NL2Bash test split (606 examples)
===================================================================
Metrics: charBLEU, template accuracy, exact match.
Run on Colab with the fine-tuned model.
"""

import subprocess
import sys

subprocess.check_call(
    [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-q",
        "transformers",
        "datasets",
        "torch",
        "nltk",
        "huggingface_hub",
    ]
)

import json
import re
import time
from collections import Counter

import nltk
import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

nltk.download("punkt_tab", quiet=True)

# ── Config ────────────────────────────────────────────────────────────────────
MODEL_ID = "AryaYT/nl2shell-0.8b"
SYSTEM_PROMPT = (
    "You are an expert shell programmer. Given a natural language request, "
    "output ONLY the corresponding shell command. No explanations."
)

# ── Load model ────────────────────────────────────────────────────────────────
print(f"Loading model: {MODEL_ID}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID, device_map="auto", torch_dtype=torch.bfloat16, trust_remote_code=True
)
model.eval()
print(f"  Device: {model.device}")


def generate_command(nl: str) -> str:
    """Generate a shell command from natural language using ChatML format."""
    prompt = (
        f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n"
        f"<|im_start|>user\n{nl}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=128,
            temperature=0.1,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    full = tokenizer.decode(outputs[0], skip_special_tokens=False)
    if "<|im_start|>assistant\n" in full:
        cmd = full.split("<|im_start|>assistant\n")[-1].split("<|im_end|>")[0].strip()
    else:
        cmd = tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1] :], skip_special_tokens=True
        ).strip()
    return cmd


# ── Metrics ───────────────────────────────────────────────────────────────────
def char_bleu(reference: str, hypothesis: str, max_n: int = 4) -> float:
    """Character-level BLEU (NLC2CMD standard)."""
    ref_chars = list(reference)
    hyp_chars = list(hypothesis)
    if not hyp_chars:
        return 0.0

    # Brevity penalty
    bp = min(1.0, len(hyp_chars) / max(len(ref_chars), 1))

    # n-gram precisions
    scores = []
    for n in range(1, max_n + 1):
        ref_ngrams = Counter(tuple(ref_chars[i : i + n]) for i in range(len(ref_chars) - n + 1))
        hyp_ngrams = Counter(tuple(hyp_chars[i : i + n]) for i in range(len(hyp_chars) - n + 1))
        clipped = sum(min(hyp_ngrams[ng], ref_ngrams[ng]) for ng in hyp_ngrams)
        total = sum(hyp_ngrams.values())
        if total == 0:
            scores.append(0.0)
        else:
            scores.append(clipped / total)

    # Geometric mean
    import math

    if any(s == 0 for s in scores):
        return 0.0
    log_avg = sum(math.log(s) for s in scores) / len(scores)
    return bp * math.exp(log_avg)


def template_match(reference: str, hypothesis: str) -> bool:
    """Template accuracy: commands match ignoring arguments (numeric, path, string values)."""

    def normalize(cmd: str) -> str:
        # Replace quoted strings, paths, numbers with placeholders
        cmd = re.sub(r'"[^"]*"', "<STR>", cmd)
        cmd = re.sub(r"'[^']*'", "<STR>", cmd)
        cmd = re.sub(r"/[\w/.\-]+", "<PATH>", cmd)
        cmd = re.sub(r"\b\d+\b", "<NUM>", cmd)
        return cmd.strip()

    return normalize(reference) == normalize(hypothesis)


def exact_match(reference: str, hypothesis: str) -> bool:
    """Exact string match after stripping."""
    return reference.strip() == hypothesis.strip()


# ── Run benchmark ─────────────────────────────────────────────────────────────
print("\nLoading NL2Bash test split (606 examples)...")
test_ds = load_dataset("GWHed/nl2bash", split="test")
print(f"  Test examples: {len(test_ds)}")

results = []
bleu_scores = []
template_correct = 0
exact_correct = 0
total = len(test_ds)

print(f"\nRunning benchmark ({total} examples)...")
start_time = time.time()

for i, row in enumerate(test_ds):
    nl = row["nl"].strip()
    ref = row["bash"].strip()

    if not nl or not ref:
        total -= 1
        continue

    pred = generate_command(nl)

    # Compute metrics
    bleu = char_bleu(ref, pred)
    tmatch = template_match(ref, pred)
    ematch = exact_match(ref, pred)

    bleu_scores.append(bleu)
    template_correct += int(tmatch)
    exact_correct += int(ematch)

    results.append(
        {
            "nl": nl,
            "reference": ref,
            "prediction": pred,
            "charBLEU": round(bleu, 4),
            "template_match": tmatch,
            "exact_match": ematch,
        }
    )

    if (i + 1) % 50 == 0 or i == 0:
        elapsed = time.time() - start_time
        avg_bleu = sum(bleu_scores) / len(bleu_scores)
        print(
            f"  [{i + 1}/{len(test_ds)}] avg charBLEU={avg_bleu:.4f} | "
            f"template={template_correct}/{i + 1} | exact={exact_correct}/{i + 1} | "
            f"{elapsed:.0f}s elapsed"
        )

elapsed = time.time() - start_time

# ── Summary ───────────────────────────────────────────────────────────────────
avg_bleu = sum(bleu_scores) / len(bleu_scores) if bleu_scores else 0
template_acc = template_correct / total if total > 0 else 0
exact_acc = exact_correct / total if total > 0 else 0

print("\n" + "=" * 60)
print(f"BENCHMARK RESULTS — NL2Shell 0.8B on NL2Bash test (n={total})")
print("=" * 60)
print(f"  charBLEU (avg):     {avg_bleu:.4f}")
print(f"  Template accuracy:  {template_acc:.4f} ({template_correct}/{total})")
print(f"  Exact match:        {exact_acc:.4f} ({exact_correct}/{total})")
print(f"  Time:               {elapsed:.0f}s ({elapsed / total:.1f}s per example)")
print("=" * 60)

# ── Comparison table ──────────────────────────────────────────────────────────
print("\n  Comparison (IC-ALFA execution accuracy):")
print("  ─────────────────────────────────────────────────")
print("  Qwen2.5-Coder-0.5B + LoRA    0.46  (Westenfelder 2025)")
print("  Llama-3.2-1B + LoRA           0.37  (Westenfelder 2025)")
print(f"  NL2Shell 0.8B (ours)          charBLEU={avg_bleu:.4f}")
print("  Note: charBLEU != IC-ALFA — not directly comparable")

# ── Save results ──────────────────────────────────────────────────────────────
with open("/content/benchmark_results.json", "w") as f:
    json.dump(
        {
            "model": MODEL_ID,
            "dataset": "GWHed/nl2bash",
            "split": "test",
            "n_examples": total,
            "metrics": {
                "charBLEU": round(avg_bleu, 4),
                "template_accuracy": round(template_acc, 4),
                "exact_match": round(exact_acc, 4),
            },
            "time_seconds": round(elapsed, 1),
            "per_example": results,
        },
        f,
        indent=2,
    )
print("\nDetailed results saved to /content/benchmark_results.json")

# ── Show 10 examples ─────────────────────────────────────────────────────────
print("\nSample predictions:")
for r in results[:10]:
    status = "✓" if r["exact_match"] else ("~" if r["template_match"] else "✗")
    print(f"  [{status}] NL:   {r['nl'][:60]}")
    print(f"       REF:  {r['reference'][:60]}")
    print(f"       PRED: {r['prediction'][:60]}")
    print(f"       BLEU: {r['charBLEU']:.4f}")
    print()
