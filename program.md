# NL2Shell Autoresearch — Program Policy

## Objective
Maximize `score` (defined below) for `AryaYT/nl2shell-0.8b` while keeping:
- Model ≤ 1.5B params
- Per-run compute < 15 Colab CU (A100)
- `eval_pass` never regresses below last best

## Composite Score
```
score = 0.60 * (1 - loss_normalized) + 0.40 * (eval_pass / 7)
```
Where `loss_normalized = loss / baseline_loss` (baseline is first run).
Higher score = better. Keep a change only if score strictly improves.

## Metrics (captured per run, written to results.tsv)
| Field | Source | Direction |
|-------|--------|-----------|
| `loss` | `trainer_stats.training_loss` | lower |
| `eval_pass` | count of 7 EVAL_PROMPTS with non-empty CMD output | higher |
| `train_time_s` | training wall-clock seconds | informational |
| `score` | composite formula above | higher |

## Target
- **HuggingFace:** `AryaYT/nl2shell-0.8b`
- **Artifacts:** merged 16-bit + GGUF (q4_k_m, q8_0)

## Hard Constraints
1. Do NOT modify `prepare.py` — it is the immutable benchmark harness
2. Do NOT modify `benchmark.py` or `experiment_gpu.py`
3. Do NOT weaken the Unsloth fallback — always keep a working transformers+PEFT path
4. Never hardcode secrets — use `HF_TOKEN` env var
5. Compute budget: < 15 CU per run (reduce epochs/batch if approaching limit)

## What You May Try (in train.py only)
- LoRA rank (8, 16, 32, 64) and alpha (lora_alpha = 2× rank is a strong default)
- Learning rate (try 1e-4, 2e-4, 5e-4) and scheduler (cosine, linear, polynomial)
- Warmup steps (5–10% of total steps)
- Batch size / gradient accumulation (keep effective batch = 32)
- Epochs (2–5; more epochs ≠ better if val loss rises)
- Optimizer (adamw_8bit, paged_adamw_32bit)
- `train_on_responses_only` — already on; try with/without
- `packing` (True/False) — packing=True improves throughput
- LoRA dropout (0.0, 0.05, 0.1)
- `max_seq_length` (256, 512, 768)
- Data augmentation: add more pairs to MACOS_PAIRS via `prepare.py` is FORBIDDEN;
  instead add augmentation INSIDE `train.py` before calling `get_dataset()`
  (e.g., shuffle, paraphrase) — but do not import from prepare.py anything not already imported

## Keep / Discard Rule
Keep a change if and only if:
1. `score` strictly improves over best previous score, AND
2. `eval_pass` does not decrease, AND
3. Training did not OOM or error

If discarded, revert `train.py` to last good commit via `git checkout train.py`.

## Logging Format (results.tsv — tab-separated)
```
timestamp\titeration\tloss\teval_pass\ttrain_time_s\tscore\tstatus\tdescription
```
`status` = KEEP or DISCARD

## Execution Loop (handled by agent_loop.sh)
1. Read `results.tsv` for current best
2. Run Copilot to propose and implement ONE change to `train.py`
3. Upload via `lecoder-cgpu copy`
4. Train via `lecoder-cgpu run python3 train.py`
5. Parse output for `loss` and `eval_pass`
6. Compute `score`
7. Keep or discard based on rule above
8. Append row to `results.tsv`
9. Repeat until MAX_ITERATIONS or stopped

## OOM Recovery
- If OOM: halve `batch_size` (min 2), double `grad_accum` (keep effective batch = 32)
- If still OOM: reduce `max_seq_length` to 256
- Log OOM as DISCARD with description "OOM - reduced batch"
