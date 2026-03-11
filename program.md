# NL2Shell Training — Program Constraints

## Budget
- **Max compute:** <15 compute units (Google Colab A100)
- **Expected:** ~3-5 CU for 3 epochs on NL2Bash (~10k examples)

## Metrics
- **Primary:** eval_loss (lower is better)
- **Qualitative:** 7 NL->shell test prompts in `prepare.py:EVAL_PROMPTS`
- **Success:** model produces syntactically valid shell commands for >=5/7 prompts

## Target
- **HuggingFace:** [AryaYT/nl2shell-0.8b](https://huggingface.co/AryaYT/nl2shell-0.8b)
- **Artifacts:** merged model + GGUF (q4_k_m, q8_0)

## Rules
1. Do NOT modify `prepare.py` — it is immutable
2. Edit only `train.py` for hyperparameter tuning or bug fixes
3. Close Colab session when training completes
4. If training loss plateaus, reduce learning rate or increase epochs
5. If OOM, reduce batch_size from 8 to 4 (keep grad_accum=4)
