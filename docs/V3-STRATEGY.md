# NL2Shell v3 — Expert-Quality Training Strategy

## Problem Statement
v1/v2 models produce "textbook" shell commands. A senior engineer types differently:

| Task | Textbook (v1/v2) | Expert (v3 target) |
|------|-------------------|-------------------|
| Check SSL cert | `openssl s_client -connect host:443` | `curl -vI https://host 2>&1 \| grep -i expire` |
| Find large files | `find / -size +100M` | `find / -size +100M -type f 2>/dev/null \| head -20` |
| Kill process on port | `lsof -i:3000 \| xargs kill -9` | `lsof -ti:3000 \| xargs kill` |
| Parse JSON API | `curl url \| grep field` | `curl -s url \| jq '.field'` |
| Disk usage | `du -sh /path` | `du -sh * \| sort -rh \| head -20` |

The difference: stderr handling, human-readable output, concise flags, proper pipe chains.

## v3 Approach: Enriched SFT (Expert Pairs Baked In)

Instead of v2 SFT → DPO as separate phases, we train a single enriched model:

```
v3 dataset = v2 dataset (11,894 pairs)
            + expert_pairs.py (300+ hand-crafted expert pairs)
            + [optional] LLM-rewritten naive pairs (500-2000)
```

### Why bake in from day one?
1. **Simpler pipeline** — one training run, not two
2. **Better gradient signal** — expert patterns mixed with bulk data prevents catastrophic forgetting
3. **Lower cost** — one A100 session instead of two
4. **DPO later if needed** — we can still add DPO on top of v3 SFT if benchmarks warrant it

## Dataset Composition

| Source | Pairs | Quality | Purpose |
|--------|-------|---------|---------|
| GWHed/nl2bash | ~8,090 | Mixed | Breadth of shell vocabulary |
| AnishJoshi/nl2bash-custom | ~3,764 (after dedup) | Mixed | Additional coverage |
| macOS synthetic | 40 | Expert | macOS-specific commands |
| **expert_pairs.py** | **300+** | **Expert** | **Senior engineer patterns** |
| LLM rewrites (optional) | 500-2,000 | High | Upgraded versions of naive pairs |
| **Total** | **~12,200-14,000** | | |

## Expert Pair Categories

1. Stderr/stdout handling (2>&1, 2>/dev/null)
2. Human-readable output (-h flags, column -t, sort -h)
3. Pipe mastery (multi-stage pipelines, awk, jq)
4. Process substitution (<(), $())
5. xargs/find expert patterns (-print0, -exec +)
6. macOS idioms (pbcopy, mdfind, caffeinate, defaults)
7. One-liner patterns (&&, ||, for loops)
8. JSON/API handling (curl -s, jq)
9. Git expert patterns (log, diff, bisect one-liners)
10. Docker/container patterns
11. Network/security (ss, ssh tunnels, nmap)
12. Text processing (awk, sed, cut, tr)
13. Modern CLI tools (fd, rg, bat, eza)

## Training Plan

```
Model:    Qwen/Qwen3.5-0.8B
Method:   QLoRA r=16, alpha=32, 4-bit NF4
Dataset:  v3 enriched (~12,200+ pairs)
Epochs:   4
Batch:    16 x 4 = 64 effective
Warmup:   5% of total steps
Hardware: A100 40GB (Colab Pro via lecoder-cgpu)
Time:     ~100 min
```

## Build Commands

```bash
# 1. Build v3 dataset
HF_TOKEN=xxx python build_v3_dataset.py --push

# 2. Train (on Colab)
HF_TOKEN=xxx python train.py  # edit to use v3 dataset

# 3. Benchmark
python benchmark.py

# Optional: LLM rewrites (costs ~$5)
ANTHROPIC_API_KEY=xxx HF_TOKEN=xxx python build_v3_dataset.py --rewrite --push
```

## Success Criteria

| Metric | v2 target | v3 target |
|--------|-----------|-----------|
| charBLEU | >0.35 | >0.45 |
| Template accuracy | >0.30 | >0.40 |
| Expert idiom rate | ~30% | >65% |
| Stderr handling | rare | standard |

## Future: DPO Phase (if v3 SFT isn't enough)

If v3 SFT alone doesn't hit targets, add DPO:
1. Run v3 model on 1,000 prompts
2. Score outputs (expert vs naive)
3. Build preference pairs from model's own outputs
4. DPO fine-tune on top of v3 (TRL DPOTrainer, beta=0.1)
5. See docs/DPO-PLAN.md for full DPO details
