# NL2Shell Prior Art — Competing Models

## CRITICAL: Original novelty claim is FALSE
"No prior sub-1B model published for NL2Bash" — INCORRECT as of Feb 2025.

## Existing Sub-1B NL2Bash Models

### Peer-Reviewed (NAACL 2025)
| Model | Params | Score (IC-ALFA) | Date |
|-------|--------|-----------------|------|
| westenfelder/Qwen2.5-Coder-0.5B-NL2SH | 500M | 0.27 | Feb 2025 |
| westenfelder/Llama-3.2-1B-NL2SH | 1B | 0.37 | Feb 2025 |
| westenfelder/Qwen2.5-Coder-1.5B-NL2SH | 1.5B | 0.50 | Feb 2025 |

### Community / Preprints
| Model | Params | Score | Date |
|-------|--------|-------|------|
| BashGemma-270M | 270M | 57.4% NLC2CMD | Dec 2025 |
| BashGPTNeo | 125M | None | ~2023 |
| CodeT5+ 220M finetune | 220M | BLEU 0.37 | May 2024 |
| T5-small NL2Bash | 60M | None | 2023 |
| GPT-2 medium NL2Bash | 345M | None | Unknown |

## Revised Novelty Claims (what IS genuinely novel)

1. **First Qwen3.5 (hybrid DeltaNet) model for NL2Bash**
   - Qwen3.5 released Feb 2026 — ALL prior work uses Qwen2.5, Llama, Gemma, T5
   - Hybrid DeltaNet architecture (75% linear + 25% softmax attention) is novel
   - This IS a genuine first — no one has used Qwen3.5 for NL2Bash

2. **Neural memory architecture analysis**
   - No prior NL2Bash paper frames the approach through neural memory theory
   - DeltaNet as associative memory + QLoRA as delta memory is original framing
   - Supported by Geva 2021, Titans 2025, but not applied to NL2Bash before

3. **macOS domain adaptation**
   - No prior model includes macOS-specific shell pairs (brew, launchctl, etc.)
   - 40 synthetic pairs for platform-specific adaptation

4. **Edge deployment benchmarks on Apple Silicon + RPi**
   - Westenfelder published GGUFs but didn't benchmark latency on specific hardware
   - First RPi 5 / Apple M-series latency measurements for NL2Bash

5. **Accuracy improvement over 0.5B baseline**
   - Westenfelder's 0.5B scored only 0.27 on IC-ALFA
   - Our 0.8B with Qwen3.5 should significantly beat this (target > 0.40)
   - If we match/exceed the 1B Llama (0.37), that's a strong result

## Updated Paper Title Options
- "NL2Shell: Leveraging Hybrid DeltaNet Attention for Efficient On-Device Shell Command Generation"
- "Beyond Softmax: NL2Shell 0.8B with Gated DeltaNet for Edge Shell Command Translation"
- "NL2Shell 0.8B: Neural Memory-Augmented Shell Command Generation via Qwen3.5 and QLoRA"

## Key Comparisons to Include in Paper
| Model | Params | Architecture | IC-ALFA |
|-------|--------|-------------|---------|
| Qwen2.5-Coder-0.5B-NL2SH | 500M | Dense transformer | 0.27 |
| BashGemma | 270M | Dense transformer | ~0.57 (NLC2CMD) |
| Llama-3.2-1B-NL2SH | 1B | Dense transformer | 0.37 |
| **NL2Shell 0.8B (ours)** | **800M** | **Hybrid DeltaNet** | **[TBD]** |
| Qwen2.5-Coder-1.5B-NL2SH | 1.5B | Dense transformer | 0.50 |
| Qwen2.5-Coder-3B-NL2SH | 3B | Dense transformer | 0.51 |
