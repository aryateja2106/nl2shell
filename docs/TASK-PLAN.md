# NL2Shell — Task Plan with Dependency Graph

## Current Status
- v1 training running on A100 (9k dataset, ETA ~58 min) — baseline model
- Research complete (benchmarks, neural memory, prior art, paper outline)
- Demo app (Gradio) ready to deploy
- Prior art found: westenfelder/Qwen2.5-Coder-0.5B-NL2SH (0.27 IC-ALFA), BashGemma-270M

## Available Compute
- Colab Pro: ~296 CU remaining (~5.37 CU/hr)
- GPUs: A100 (40GB), H100 (80GB), L4, T4
- H100 recommended for v2 training (2x faster, more VRAM for larger batches)

---

## Task Dependency Graph

```
[T1] v1 baseline training (RUNNING)
  |
  v
[T2] v1 evaluation + benchmarks ──────────────────┐
  |                                                 |
  v                                                 v
[T3] Prepare v2 dataset (20k+)         [T6] Deploy HF Space demo
  |                                                 |
  v                                                 v
[T4] v2 training on H100 (improved)    [T7] Publish v1 to HuggingFace
  |
  v
[T5] v2 evaluation + benchmarks
  |
  v
[T8] Write research paper (arXiv)
  |
  v
[T9] Publish everything (HF, GitHub, arXiv)
```

---

## Tasks

### T1: v1 Baseline Training [RUNNING] [NO BLOCKER]
- Status: 10/765 steps, ~58 min remaining on A100
- Dataset: GWHed/nl2bash (8,090 train) + 40 macOS pairs
- Config: QLoRA r=16, alpha=32, 3 epochs, batch 32
- Output: baseline model for comparison

### T2: v1 Evaluation + Benchmarks [BLOCKED BY T1]
- Run `run_eval()` (7 test prompts) — already in train.py
- Download model from HuggingFace
- Evaluate on NL2Bash test split (606 examples) — charBLEU, template acc, exact match
- Compare against: Qwen2.5-Coder-0.5B-NL2SH (0.27 IC-ALFA)
- Record training loss, eval scores

### T3: Prepare v2 Dataset [DONE ✓]
- Combined datasets (actual results):
  - GWHed/nl2bash: 6,400 unique (of 8,090 raw)
  - AnishJoshi/nl2bash-custom: 5,455 unique (of 19,658 raw — 57% overlap with GWHed)
  - macOS synthetic: 39 (1 was a duplicate)
  - **Total after dedup: 11,894 unique pairs** (47% increase over v1's 8,130)
- Formatted as ChatML, pushed to AryaYT/nl2shell-training
- Live at: https://huggingface.co/datasets/AryaYT/nl2shell-training

### T4: v2 Training on H100 [BLOCKED BY T1 — notebook ready]
- Notebook: `nl2shell-v2-train.ipynb` (10 cells, H100 HIGHMEM)
- Hyperparameters (revised per Amp review — r=32 overfits on 12k):
  - LoRA rank: r=16, alpha=32 (same as v1 — prevents overfitting)
  - Epochs: 4 (slight increase from v1's 3)
  - Batch: 16 x 4 = 64 effective (H100 headroom)
  - Warmup: 5% of total steps
  - Response-only masking + train_on_responses_only
- 11,894 examples, 4 epochs → ~744 steps
- Est. time: ~1 hour on H100 (~5 CU)
- Export: GGUF q4_k_m + q8_0
- Push to AryaYT/nl2shell-0.8b (overwrite v1)

### T5: v2 Evaluation + Benchmarks [BLOCKED BY T4]
- Full benchmark suite:
  - NL2Bash test split (606 examples): charBLEU, template acc, exact match
  - IC-ALFA test set (600 examples) if accessible
  - 7 qualitative eval prompts
  - macOS-specific eval (40 synthetic test prompts)
- Compare against baselines:
  | Model | IC-ALFA |
  |-------|---------|
  | Qwen2.5-Coder-0.5B-NL2SH | 0.27 |
  | Llama-3.2-1B-NL2SH | 0.37 |
  | BashGemma-270M | 0.57 (NLC2CMD) |
  | **NL2Shell 0.8B v2 (ours)** | **target > 0.40** |
- Edge benchmarks (if RPi available): tokens/sec, TTFT, memory usage

### T6: Deploy HF Space Demo [BLOCKED BY T1 or T4 (whichever finishes)]
- Push app.py, requirements.txt, SPACE_README.md to HF Space
- Create Space: AryaYT/nl2shell-demo (Gradio SDK)
- Test on CPU (free tier)
- Optionally enable ZeroGPU if HF PRO available

### T7: Publish v1 to HuggingFace [BLOCKED BY T1]
- Already handled by train.py (auto-pushes)
- Verify model card, GGUF files uploaded
- Add tags: nl2bash, shell, terminal, qwen3.5, qlora

### T8: Write Research Paper [BLOCKED BY T5]
- Use paper-outline.md as structure
- Use research-neural-memory.md for Section 3 (architecture)
- Use research-benchmarks.md for Section 2 (related work)
- Use research-prior-art.md for honest novelty claims
- Key sections: Abstract, Intro, Related Work, Method, Experiments, Results, Discussion
- Figures: architecture diagram, loss curves, benchmark bar chart
- Target: 4-6 pages, ACL short paper format
- Tools: Overleaf + ACL template

### T9: Publish Everything [BLOCKED BY T8]
- arXiv submission (cs.CL + cs.SE)
- GitHub: push nl2shell/ code to cloudagi repo
- HuggingFace: final model + model card linking paper
- HF Space: demo live
- Announce: Twitter, HuggingFace blog post

---

## Compute Budget

| Task | GPU | Est. CU | Est. Time |
|------|-----|---------|-----------|
| T1 v1 training | A100 | ~5 CU | ~1 hr |
| T4 v2 training | H100 | ~10 CU | ~2 hr |
| T5 benchmarks | A100/L4 | ~2 CU | ~30 min |
| **Total** | | **~17 CU** | **~3.5 hr** |

Remaining after: ~280 CU (plenty of headroom)

---

## Agent Assignment

| Task | Agent Type | Can Parallelize? |
|------|-----------|-----------------|
| T1 | Running (lecoder-cgpu) | N/A |
| T2 | engineer | After T1 |
| T3 | engineer | YES — start now |
| T4 | engineer (Colab) | After T3 |
| T5 | engineer | After T4 |
| T6 | engineer | After T1 |
| T7 | auto (train.py) | After T1 |
| T8 | researcher + engineer | After T5 |
| T9 | engineer | After T8 |
