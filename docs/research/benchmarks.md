# NL2Bash Benchmarks & Related Work — Research Notes

## Datasets

### NL2Bash (Lin et al., 2018) — PRIMARY
- 9,305 total pairs, 102 bash utilities, 206 flags
- Split: 8,090 train / 609 dev / 606 test
- HuggingFace: jiacheng-ye/nl2bash
- Use 606-example test split for backward compatibility

### NL2SH-ALFA (Westenfelder & Finn, NAACL 2025) — CURRENT STANDARD
- 600 manually verified test pairs (dual ground truth)
- 40,639 combined training pairs
- HuggingFace: westenfelder/NL2SH-ALFA
- Difficulty split: easy / medium / hard

### InterCode-Bash (Yang et al., NeurIPS 2023)
- 224 instruction-command pairs (111 valid)
- Docker-based execution evaluation

### IBM nl2bash-eabench (2024)
- 125 hand-crafted test cases (50 single-line, 50 multi-line, 25 PowerShell)
- Container-based execution

## Evaluation Metrics (what to report)

1. **Execution-based accuracy** (IC-ALFA) — gold standard since 2024
2. **Character-level BLEU** — legacy compatibility
3. **Template accuracy** — structural match ignoring args
4. **Exact match** — strict string equality

## State of the Art (IC-ALFA, 600 examples)

| Model | Params | Base | + LoRA |
|-------|--------|------|--------|
| GPT-4o | ~1.8T | **0.74** | — |
| GPT-4o-mini | ~? | ~0.65 | — |
| GPT-3.5-turbo | ~? | ~0.55 | — |
| Qwen2.5-Coder-7B | 7B | 0.61 | — |
| Qwen2.5-Coder-3B | 3B | 0.44 | 0.51 |
| Llama-3.1-8B | 8B | 0.46 | 0.40 |
| Llama-3.2-3B | 3B | 0.24 | 0.51 |
| Qwen2.5-Coder-1.5B | 1.5B | ~0.32 | ~0.50 |
| **Qwen2.5-Coder-0.5B** | **0.5B** | **~0.20** | **~0.46** |
| Llama-3.2-1B | 1B | 0.12 | 0.37 |

**KEY: Fine-tuning closes a 1-2B gap in model scale.**

## Most Comparable Baseline

Qwen2.5-Coder-0.5B + LoRA = ~0.46 on IC-ALFA
Our Qwen3.5-0.8B should target > 0.46, ideally matching 1.5B (~0.50)

## IBM Execution-Based Scores (single-line Bash)

| Model | 0-shot | 5-shot | 10-shot |
|-------|--------|--------|---------|
| GPT-4o | 84% | 86% | 88% |
| CodeLlama-34B | 70% | 68% | 64% |
| Mistral-7B | 62% | 54% | 58% |
| Granite-20B | 64% | 64% | 74% |

## Key Papers (chronological)

1. Lin et al. (2018) — NL2Bash dataset + Tellina (LREC, arXiv:1802.08979)
2. Agarwal et al. (2021) — NLC2CMD NeurIPS competition (arXiv:2103.02523)
3. Zhang et al. (2023) — Coder Reviewer Reranking (ICML, arXiv:2211.16490)
4. Agarwal et al. (2023) — NL2CMD updated workflow (arXiv:2302.07845)
5. Yang et al. (2023) — InterCode benchmark (NeurIPS, arXiv:2306.14898)
6. Vo et al. (2024) — IBM execution-based eval (arXiv:2405.06807)
7. Khoury et al. (2024) — ScriptSmith (arXiv:2409.17166)
8. Westenfelder & Finn (2025) — NL2SH-ALFA, IC-ALFA (NAACL, arXiv:2502.06858)

## Novelty Confirmation

**No prior published paper fine-tunes a sub-1B model specifically for NL2Bash as a standalone research contribution.** Westenfelder & Finn (2025) evaluated Qwen2.5-Coder-0.5B as one of many models, but did not publish it as a dedicated artifact. Our NL2Shell 0.8B would be the first.

## Safety Evaluation

- No standardized safety benchmark exists for NL2Bash
- Recommend: blocklist of dangerous patterns (rm -rf /, dd, fork bombs)
- All execution eval in sandboxed Docker containers
- Cite IBM rootless container approach
