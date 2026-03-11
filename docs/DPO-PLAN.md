# NL2Shell — DPO Fine-Tuning Plan (v3)

## Problem
v1/v2 models produce "textbook" shell commands but miss expert patterns:
- Missing `2>&1` redirects (curl -v outputs to stderr)
- Verbose flags instead of short forms
- Naive piping (doesn't account for stderr vs stdout)
- Missing common idioms (jq, xargs -0, process substitution)

## Strategy: SFT → DPO Pipeline

### Phase 1: Preference Dataset (2,000-5,000 pairs)

Format: `{prompt, chosen, rejected}`

**Method A: Frontier model rewriting**
1. Take all 11,894 NL2Bash pairs
2. Send to Claude/GPT-4: "Given this NL request, here's a naive command. Rewrite it as an expert would — concise, proper redirects, idiomatic."
3. Original = rejected, rewritten = chosen

**Method B: Hand-curated expert pairs (200-500)**
Focus on patterns the model consistently gets wrong:

| Pattern | Naive (rejected) | Expert (chosen) |
|---------|------------------|-----------------|
| stderr redirect | `curl -v url \| grep cert` | `curl -vI url 2>&1 \| grep cert` |
| silence errors | `find / -name foo` | `find / -name foo 2>/dev/null` |
| process kill | `lsof -i:3000 \| xargs kill -9` | `lsof -ti:3000 \| xargs kill` |
| json parsing | `curl url \| grep field` | `curl -s url \| jq '.field'` |
| file listing | `find . -type f -exec ls -s {} \;` | `ls -lhS` or `du -sh * \| sort -rh` |
| disk usage | `du -sh /path/to/dir` | `du -sh * \| sort -rh \| head -20` |
| process by port | `netstat -tlnp \| grep 8080` | `lsof -ti:8080` |
| clipboard | `cat file` | `cat file \| pbcopy` (macOS) |
| watch changes | `while true; do ls; sleep 1; done` | `fswatch .` or `watch -n1 ls` |
| git log | `git log --oneline` | `git log --oneline -20` |

**Method C: Contrastive pairs from model output**
1. Run v2 model on 1,000 prompts
2. Manually score outputs as good/bad
3. For bad ones, write the expert version
4. Use as preference pairs

### Phase 2: DPO Training

```python
from trl import DPOTrainer, DPOConfig

# Load v2 model (already SFT'd)
model = FastLanguageModel.from_pretrained("AryaYT/nl2shell-0.8b", ...)
ref_model = None  # Use implicit reference (beta controls divergence)

dpo_config = DPOConfig(
    beta=0.1,                    # KL penalty (0.1-0.5, start low)
    learning_rate=5e-6,          # Much lower than SFT
    num_train_epochs=2,          # DPO needs fewer epochs
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    bf16=True,
    loss_type="sigmoid",         # Standard DPO loss
    max_length=512,
    max_prompt_length=256,
)

trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,
    args=dpo_config,
    train_dataset=preference_dataset,
    tokenizer=tokenizer,
)
trainer.train()
```

### Phase 3: Expert Idioms SFT Boost (optional)

If DPO alone isn't enough, do a final SFT pass on 200-500 hand-crafted
expert pairs. This is "knowledge distillation" from senior engineers.

Categories:
- **stderr/stdout management** (50 pairs)
- **Process management** (40 pairs)
- **File operations** (40 pairs)
- **Network/HTTP** (40 pairs)
- **Git workflows** (30 pairs)
- **macOS-specific** (30 pairs)
- **Docker/containers** (20 pairs)
- **Text processing** (jq, awk, sed — 30 pairs)
- **System monitoring** (20 pairs)

## Expected Impact

| Metric | v2 (SFT only) | v3 (SFT + DPO) |
|--------|---------------|-----------------|
| IC-ALFA | ~0.40 | target >0.55 |
| Expert idioms | ~30% | target >70% |
| Stderr handling | rare | common |
| Conciseness | verbose | idiomatic |

## Compute Budget
- Preference dataset generation: ~$5 (Claude API for 5k rewrites)
- DPO training: ~5 CU on A100 (~1 hour)
- Expert SFT boost: ~2 CU on A100 (~30 min)
- Total: <$15 + ~7 CU

## Timeline
1. Complete v2 SFT training (current — ~100 min remaining)
2. Run v2 benchmarks (IC-ALFA, charBLEU on 606 test examples)
3. Build preference dataset (1-2 days)
4. DPO training (1 hour)
5. v3 benchmarks (compare against v2)
6. Paper: report SFT→DPO improvement as key result

## References
- Rafailov et al. (2023): DPO — arxiv:2305.18290
- TRL DPOTrainer: https://huggingface.co/docs/trl/dpo_trainer
- Tunstall et al. (2023): Zephyr — SFT + DPO on 7B model
