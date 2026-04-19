---
dataset_info:
  features:
    - name: text
      dtype: string
    - name: nl
      dtype: string
    - name: bash
      dtype: string
    - name: source
      dtype: string
  splits:
    - name: train
      num_examples: 12834
license: apache-2.0
task_categories:
  - text-generation
language:
  - en
size_categories:
  - 10K<n<100K
tags:
  - nl2bash
  - shell
  - command-line
  - code-generation
  - fine-tuning
  - chatml
  - qwen
  - edge-ai
pretty_name: NL2Shell Training v3
---

# NL2Shell Training Dataset v3

**12,834 natural-language-to-shell-command pairs for fine-tuning local code models.**

Trained model: [AryaYT/nl2shell-0.8b](https://huggingface.co/AryaYT/nl2shell-0.8b) | Live demo: [AryaYT/nl2shell-demo](https://huggingface.co/spaces/AryaYT/nl2shell-demo)

## Overview

This dataset maps plain English descriptions to their corresponding shell (bash) commands. It is designed for fine-tuning small language models (0.5B-3B parameters) to run locally on consumer hardware — translating natural language into executable shell commands in under a second, fully offline.

## Dataset Structure

Each row contains four columns:

| Column | Type | Description |
|--------|------|-------------|
| `text` | string | Full ChatML-formatted training example (system + user + assistant turns) |
| `nl` | string | Natural language description of the desired command |
| `bash` | string | The corresponding shell command |
| `source` | string | Provenance of the pair (see Sources below) |

### ChatML Format

The `text` column is pre-formatted in ChatML for direct use with Qwen, Llama, and other models that support the `<|im_start|>` / `<|im_end|>` template:

```
<|im_start|>system
You are an expert shell programmer. Given a natural language request, output ONLY the corresponding shell command. No explanations.<|im_end|>
<|im_start|>user
find all python files modified today<|im_end|>
<|im_start|>assistant
find . -name "*.py" -mtime -1<|im_end|>
```

## Sources

| Source | Count | Percentage | Description |
|--------|-------|------------|-------------|
| [GWHed/nl2bash](https://huggingface.co/datasets/GWHed/nl2bash) | 6,392 | 49.8% | Academic NL2Bash corpus — broad coverage of core Unix utilities |
| [AnishJoshi/nl2bash-custom](https://huggingface.co/datasets/AnishJoshi/nl2bash-custom) | 5,450 | 42.5% | Community-contributed bash pairs with diverse command patterns |
| Expert-curated | 961 | 7.5% | Senior-engineer-quality commands written by multiple AI agents (Amp, Codex, Gemini, Cursor) and hand-verified |
| macOS-synthetic | 31 | 0.2% | macOS-specific commands (`open`, `pbcopy`, `defaults`, `diskutil`, etc.) |

**Total: 12,834 unique pairs** (deduplicated by bash command, expert pairs take priority on conflicts).

### What's in the expert-curated pairs?

The 961 expert pairs cover advanced shell patterns that typical NL2Bash datasets miss:

- **I/O redirection & process substitution** — `exec 3>&1`, `tee >(grep ...)`, `diff <(cmd1) <(cmd2)`
- **Git advanced workflows** — worktrees, reflog recovery, sparse checkout, `git log -S/-G`
- **Kubernetes operations** — `kubectl exec`, `rollout status`, CrashLoopBackOff filtering
- **Cloud CLI** — AWS (`ec2`, `lambda`, `s3`, `secretsmanager`), GCP (`gcloud run`, `compute`)
- **Database operations** — PostgreSQL (`psql -c`, `pg_stat_activity`), SQLite, MySQL
- **Docker & Compose** — multi-stage builds, volume mounts, health checks, `docker system prune`
- **Networking & security** — `openssl`, `nmap`, `tcpdump`, `iptables`, `ssh` tunneling
- **Performance profiling** — `perf`, `strace`, `time`, `/proc` filesystem
- **Text processing** — `awk`, `sed`, `jq`, `xargs`, `parallel`
- **macOS-specific** — `pbcopy`, `open`, `defaults`, `launchctl`, `diskutil`

## How to Use

### Load with HuggingFace Datasets

```python
from datasets import load_dataset

ds = load_dataset("AryaYT/nl2shell-training-v3", split="train")
print(ds[0])
# {'text': '<|im_start|>system\n...', 'nl': '...', 'bash': '...', 'source': '...'}
```

### Fine-tune with TRL (SFT)

```python
from datasets import load_dataset
from trl import SFTTrainer, SFTConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "Qwen/Qwen2.5-Coder-1.5B"
ds = load_dataset("AryaYT/nl2shell-training-v3", split="train")

model = AutoModelForCausalLM.from_pretrained(model_id)
tokenizer = AutoTokenizer.from_pretrained(model_id)

trainer = SFTTrainer(
    model=model,
    train_dataset=ds,
    args=SFTConfig(
        output_dir="./nl2shell-ft",
        num_train_epochs=4,
        per_device_train_batch_size=8,
        gradient_accumulation_steps=8,
        learning_rate=2e-4,
        bf16=True,
    ),
    processing_class=tokenizer,
)
trainer.train()
```

### Fine-tune with QLoRA (memory-efficient)

```python
from peft import LoraConfig

peft_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    task_type="CAUSAL_LM",
)

# Pass peft_config to SFTTrainer for 4-bit QLoRA training
# Recommended: H100/A100 GPU, ~4 epochs, batch size 64 (via gradient accumulation)
```

### Query with SQL (DuckDB)

```sql
SELECT source, COUNT(*) as count
FROM 'hf://datasets/AryaYT/nl2shell-training-v3@~parquet/default/train/*.parquet'
GROUP BY source
ORDER BY count DESC;
```

## Dataset Construction

Built by [`build_v3_dataset.py`](https://github.com/aryateja2106/cloudagi):

1. **Load v2** — Pulls 11,894 pairs from [AryaYT/nl2shell-training](https://huggingface.co/datasets/AryaYT/nl2shell-training)
2. **Load expert pairs** — 1,009 senior-engineer-quality pairs from `expert_pairs.py`
3. **Concatenate** — Expert pairs placed first (higher priority)
4. **Normalize** — Strip whitespace, drop empty/NaN rows
5. **Deduplicate** — By `bash` column, `keep="first"` (expert pairs win conflicts)
6. **Format** — Each pair wrapped in ChatML template
7. **Result** — 12,834 unique pairs (69 duplicates removed)

### Deduplication Strategy

Deduplication is by the `bash` command column only (not the NL description). When multiple sources provide the same shell command with different natural language descriptions, the expert-curated description is kept. This ensures the highest-quality NL phrasing for commands that appear in multiple source datasets.

## Version History

| Version | Rows | Changes |
|---------|------|---------|
| v1 | 8,130 | GWHed/nl2bash + 40 macOS pairs |
| v2 | 11,894 | Added AnishJoshi/nl2bash-custom, deduplication |
| **v3** | **12,834** | **+961 expert-curated pairs, ChatML formatting, multi-source pipeline** |

## Recommended Base Models

| Model | Parameters | Ollama Compatible | Notes |
|-------|-----------|-------------------|-------|
| Qwen2.5-Coder-1.5B | 1.5B | Yes | Best balance of quality and speed for edge deployment |
| Qwen2.5-Coder-0.5B | 0.5B | Yes | Fastest, fits on Raspberry Pi |
| Qwen2.5-Coder-3B | 3B | Yes | Highest quality, needs 4GB+ RAM |
| Qwen3.5-0.8B | 0.8B | No (unsupported architecture) | Used for v1 training; hybrid DeltaNet not yet in Ollama's GGUF loader |

## Evaluation

Benchmark script available at `benchmark.py` in the source repo. Metrics:

- **charBLEU** — Character-level BLEU score (captures partial command matches)
- **Template accuracy** — Correct command structure with different arguments
- **Exact match** — Strict string equality on 606 held-out test examples

## License

Apache 2.0 — use freely for research and commercial applications.

## Citation

```bibtex
@dataset{nl2shell_v3_2026,
  author = {Arya Teja},
  title = {NL2Shell Training Dataset v3},
  year = {2026},
  publisher = {HuggingFace},
  url = {https://huggingface.co/datasets/AryaYT/nl2shell-training-v3}
}
```

## Related Resources

- **Model**: [AryaYT/nl2shell-0.8b](https://huggingface.co/AryaYT/nl2shell-0.8b) — Fine-tuned Qwen3.5 (v1 training)
- **Demo**: [AryaYT/nl2shell-demo](https://huggingface.co/spaces/AryaYT/nl2shell-demo) — Try it in your browser
- **CLI**: [Vox](https://github.com/aryateja2106/vox) — Terminal client that uses this model
- **v2 Dataset**: [AryaYT/nl2shell-training](https://huggingface.co/datasets/AryaYT/nl2shell-training) — Previous version
