# NL2Shell — Agent Instructions

Repository: https://github.com/nl2shell/nl2shell
Part of the [nl2shell org](https://github.com/nl2shell) — 5 repos, one product.

---

## Project Overview

**nl2shell** is the core ML training repository for NL2Shell: a fine-tuned
Qwen3.5-0.8B model that converts plain English into executable shell commands.

- Model: `AryaYT/nl2shell-0.8b` on HuggingFace — 859M params, GGUF-ready
- Architecture: Hybrid DeltaNet (75% linear + 25% softmax attention)
- Training method: QLoRA (r=16, alpha=32, NF4 4-bit, response-only loss masking)
- Dataset: 12,834 NL-to-bash pairs (v2 base + expert-curated additions)
- Output: plain shell command only — no markdown, no explanation

---

## Repo Structure

```
nl2shell/
├── prepare.py              # IMMUTABLE — dataset loader, ChatML formatter, eval harness
├── train.py                # QLoRA fine-tuning (only file you should edit)
├── benchmark.py            # charBLEU / template accuracy / exact match eval (IMMUTABLE)
├── build_v2_dataset.py     # Builds v2 dataset: dedup, merge, push to HF
├── build_v3_dataset.py     # Builds v3 dataset: v2 + expert pairs + optional LLM rewrites
├── expert_pairs.py         # 1009 senior-engineer-quality (nl, cmd) pairs
├── experiment_gpu.py       # GPU memory profiling (IMMUTABLE)
├── app.py                  # Gradio demo — runs locally and on HF Spaces
├── agent_loop.sh           # Autoresearch loop: propose → train → evaluate → keep/discard
├── deploy-space.sh         # Deploy app.py to HuggingFace Spaces
├── Modelfile               # Ollama Modelfile for hf.co/AryaYT/nl2shell-0.8b
├── program.md              # Autoresearch policy: scoring, constraints, budget
├── results.tsv             # Training run history (loss, eval_pass, score)
├── pyproject.toml          # uv project config with dependency groups
├── docs/
│   ├── RUNBOOK.md          # Copy-paste commands for the full training workflow
│   ├── TASK-PLAN.md        # T1-T9 task dependency graph
│   └── research/           # Prior art, benchmark notes, architecture notes
├── paper/
│   └── nl2shell.tex        # ACL short paper (LaTeX)
└── notebooks/
    ├── train-v1.ipynb      # v1 training run (A100, 8,130 pairs)
    └── train-v2.ipynb      # v2 training run (H100, 11,894 pairs)
```

### Immutable files — never modify

| File | Why |
|------|-----|
| `prepare.py` | Benchmark harness and dataset formatter. Changing it invalidates comparisons. |
| `benchmark.py` | Evaluation script. Results must be reproducible across runs. |
| `experiment_gpu.py` | GPU profiling reference. Results must be consistent. |

---

## Build and Test Commands

This project uses [uv](https://docs.astral.sh/uv/) for package management.

```bash
# Install dev tools (ruff, ty)
uv sync --group dev

# Lint
uv run ruff check src/

# Format
uv run ruff format .

# Type check
uv run ty check .

# Run tests
uv run pytest

# Install all dependency groups at once
uv sync --group train --group eval --group demo --group data --group dev
```

### Per-workflow installs

```bash
uv sync --group train   # QLoRA fine-tuning (requires CUDA GPU)
uv sync --group eval    # benchmark.py evaluation
uv sync --group demo    # Gradio demo (app.py)
uv sync --group data    # dataset pipeline scripts
```

---

## Dataset Pipeline

Four scripts form the full pipeline, run in order:

```
prepare.py  →  build_v3_dataset.py  →  train.py  →  benchmark.py
```

### Step 1: prepare.py (read-only utility)

Provides `get_dataset()`, `format_chatml()`, `run_eval()`, and `EVAL_PROMPTS`.
Import from here in `train.py`. Never modify.

### Step 2: build_v3_dataset.py — assemble training data

```bash
export HF_TOKEN=hf_...

# Build v3: v2 base (11,894 pairs) + expert pairs (1009) + dedup
python build_v3_dataset.py --push

# Save locally as parquet instead
python build_v3_dataset.py --local

# Add LLM rewrites via Claude API (costs credits)
export ANTHROPIC_API_KEY=sk-ant-...
python build_v3_dataset.py --push --rewrite
```

The v3 builder merges three sources in priority order:
1. `expert_pairs.py` — 1009 handcrafted senior-engineer commands (highest priority)
2. v2 HuggingFace dataset — 11,894 deduplicated pairs from NL2Bash benchmarks
3. LLM rewrites via Claude (optional, lowest priority)

Deduplication is by bash command; expert pairs win on conflict.

### Step 3: train.py — QLoRA fine-tuning

```bash
uv sync --group train
export HF_TOKEN=hf_...
python train.py
```

Training runs on Google Colab A100 via `lecoder-cgpu`:
```bash
lecoder-cgpu copy train.py
lecoder-cgpu copy prepare.py
lecoder-cgpu run python3 train.py
```

Hyperparameter tuning is guided by `program.md`. The autoresearch loop in
`agent_loop.sh` automates propose → train → score → keep/discard iterations.

### Step 4: benchmark.py — evaluate

```bash
uv sync --group eval
python benchmark.py
# Writes per-example predictions to benchmark_results.json
```

Metrics on 606 NL2Bash test examples:
- **charBLEU** — character-level BLEU-4 with brevity penalty
- **Template accuracy** — match after normalizing quoted strings and paths
- **Exact match** — identical string after stripping whitespace

---

## Environment Variables

| Variable | Required for | Notes |
|----------|-------------|-------|
| `HF_TOKEN` | `train.py`, `build_*.py --push` | HuggingFace write token. Never hardcode. |
| `ANTHROPIC_API_KEY` | `build_v3_dataset.py --rewrite` | Only needed for LLM rewrites. |

---

## Autoresearch Loop (program.md)

The `agent_loop.sh` script runs an automated improvement cycle:

1. Read `results.tsv` for current best score
2. Propose and implement one change to `train.py`
3. Upload and train on Colab via `lecoder-cgpu`
4. Parse output for `loss` and `eval_pass`
5. Compute composite score: `0.60 * (1 - loss_normalized) + 0.40 * (eval_pass / 7)`
6. Keep if score improves and `eval_pass` does not decrease; otherwise discard
7. Append row to `results.tsv`

What you may change in `train.py`: LoRA rank/alpha/dropout, learning rate,
scheduler, batch size, gradient accumulation, epochs, optimizer, sequence
packing, max_seq_length.

OOM recovery: halve batch size, double gradient accumulation (keep effective
batch = 32). If still OOM, reduce max_seq_length to 256.

---

## Contributing

### Adding training pairs

The fastest way to improve the model is to add high-quality pairs to
`expert_pairs.py`. Each entry is a `(natural_language, bash_command)` tuple.

Guidelines:
- Write the command the way a senior engineer would: idiomatic flags,
  proper quoting, pipelines where appropriate
- Prefer one-liners over multi-command scripts
- Include macOS-specific, Kubernetes, cloud CLI, and niche tool coverage —
  these are underrepresented in the base NL2Bash dataset
- Avoid duplicating commands already in `expert_pairs.py`

Then rebuild the v3 dataset and retrain:
```bash
python build_v3_dataset.py --local   # verify your pairs appear
python build_v3_dataset.py --push    # publish to HF
python train.py                      # retrain
python benchmark.py                  # verify no regression
```

### Running benchmarks

```bash
uv sync --group eval
python benchmark.py
```

Open an issue with your results: hardware, model version (check HF commit),
charBLEU, template accuracy, exact match. Results from different hardware help
calibrate inference latency claims.

### Conventions

- Python 3.10+
- Ruff for lint and format (`ruff check .` + `ruff format .`)
- `ty` for type checking
- Conventional commits: `type(scope): description`
- All HuggingFace tokens via `HF_TOKEN` env var — never hardcode secrets
- Scripts are standalone — no cross-imports between scripts

---

## nl2shell Org — Cross-References

NL2Shell is a 5-repo organization. This repo (the ML core) feeds into all of them.

| Repo | GitHub | Role |
|------|--------|------|
| **nl2shell** (this) | https://github.com/nl2shell/nl2shell | Core ML: training, dataset, benchmarks |
| **nl2shell-web** | https://github.com/nl2shell/nl2shell-web | Next.js website at nl2shell.com, includes an MCP server exposing the model as a tool |
| **vox** | https://github.com/nl2shell/vox | Voice-powered CLI: speak a description, get a shell command, execute in terminal |
| **sandbox-bash-mcp** | https://github.com/nl2shell/sandbox-bash-mcp | Docker-based sandboxed bash execution exposed via MCP protocol |
| **collab** | https://github.com/nl2shell/collab | Electron desktop app with infinite canvas for terminal orchestration |

### How the model flows downstream

```
nl2shell (training) ──► HuggingFace model (AryaYT/nl2shell-0.8b)
                              │
              ┌───────────────┼──────────────────────────────┐
              ▼               ▼                              ▼
        nl2shell-web         vox                          collab
     (MCP server +       (voice CLI)            (Electron canvas app)
      website demo)
              │
              ▼
     sandbox-bash-mcp
     (safe execution layer)
```

When the model is updated and pushed to HuggingFace, consumers pick up the new
version on their next model load. No cross-repo code changes are required for
a model update.

### Integration points for agents working across repos

- **nl2shell-web MCP server**: exposes the model via MCP for any MCP-compatible
  client. See https://github.com/nl2shell/nl2shell-web for the server spec.
- **sandbox-bash-mcp**: provides safe execution of generated commands.
  Pair with this repo's output when building test harnesses that execute commands.
  See https://github.com/nl2shell/sandbox-bash-mcp.
- **vox**: voice input pipeline for the model. If adding new command domains
  (Kubernetes, cloud CLIs), coordinate with vox to ensure voice recognition
  handles the terminology. See https://github.com/nl2shell/vox.

---

## HuggingFace Resources

| Resource | URL |
|----------|-----|
| Model | https://huggingface.co/AryaYT/nl2shell-0.8b |
| Dataset v2 | https://huggingface.co/datasets/AryaYT/nl2shell-training |
| Dataset v3 | https://huggingface.co/datasets/AryaYT/nl2shell-training-v3 |
| Demo (Gradio) | https://huggingface.co/spaces/AryaYT/nl2shell-demo |
| Base model | https://huggingface.co/Qwen/Qwen3.5-0.8B |
| NL2Bash dataset | https://huggingface.co/datasets/GWHed/nl2bash |
