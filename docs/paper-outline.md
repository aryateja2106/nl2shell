# NL2Shell 0.8B — Research Paper Outline

## Title
"NL2Shell 0.8B: Hybrid DeltaNet Attention for Efficient On-Device Shell Command Generation"

Alternative: "Beyond Softmax: Neural Memory-Augmented Shell Command Generation with Qwen3.5 and QLoRA"

## Target Venues
1. arXiv cs.CL + cs.SE (immediate, establish priority)
2. ENLSP @ NeurIPS 2026 (Aug deadline) — efficiency + small models
3. EMNLP 2026 short paper track (June deadline)

## Format
4-6 pages, ACL short paper style, ~2,500-4,000 words + tables/figures

---

## Abstract (~150 words)
- Task: NL-to-shell translation
- Problem: existing sub-1B models (Westenfelder 2025, 0.27 IC-ALFA) use dense transformers; hybrid architectures unexplored
- Method: Qwen3.5-0.8B + QLoRA (r=16, alpha=32, 4-bit) on NL2Bash (9,305) + 40 macOS pairs
- Training: ChatML, response-only loss masking, 3 epochs, cosine LR
- Results: [fill after training] competitive with 10x larger models
- Export: GGUF q4_k_m/q8_0, runs offline on RPi 5 / Apple Silicon

## 1. Introduction (~0.5 page)
- Hook: shell syntax is unforgiving, developers lose time translating intent
- Problem: existing NL2Bash assistants require cloud APIs
- Gap: no sub-1B fine-tuned model with edge deployment validation

### Research Questions
- RQ1: Can sub-1B achieve competitive NL2Bash accuracy?
- RQ2: Does macOS domain adaptation help on Apple workloads?
- RQ3: What's the inference profile on constrained hardware?

### Contributions
1. Smallest published fine-tuned NL2Bash model
2. QLoRA recipe applicable to any sub-1B code model
3. macOS shell command augmentation (40 pairs)
4. GGUF edge deployment with latency benchmarks
5. Open weights + code (MIT): AryaYT/nl2shell-0.8b

## 2. Related Work (~0.5 page)
- **NL2Shell translation:** Tellina/Lin 2018, NLC2CMD NeurIPS 2020, NL2CMD Mukherjee 2023, LLM-NL2Bash Westenfelder NAACL 2025, IBM NL2Bash-EAbench 2024
- **Efficient fine-tuning:** LoRA (Hu 2021), QLoRA (Dettmers 2023), Unsloth
- **Small code models:** CodeT5 (220M), Qwen3.5 family, Phi-2, Gemma-2
- **Edge deployment:** llama.cpp/GGUF, Ollama, LEAF framework

## 3. The NL2Shell 0.8B System (~1 page)

### 3.1 Base Model Selection
- Qwen3.5-0.8B: smallest in family, Apache 2.0, native ChatML, 262K context

### 3.2 Dataset

| Source | Examples | Domain |
|--------|----------|--------|
| NL2Bash (jiacheng-ye/nl2bash) | 9,305 | General Linux/bash |
| macOS Synthetic (hand-crafted) | 40 | macOS-specific tools |
| **Total** | **9,345** | |

### 3.3 Training Configuration

| Parameter | Value |
|-----------|-------|
| Quantization | 4-bit NF4 |
| LoRA rank | 16 |
| LoRA alpha | 32 |
| Target modules | All linear (q,k,v,o,gate,up,down) |
| Dropout | 0.05 |
| Epochs | 3 |
| Effective batch | 32 (8 x 4 grad accum) |
| LR | 2e-4, cosine |
| Loss masking | Response-only |
| Packing | Enabled |
| Hardware | A100 40GB |

### 3.4 Neural Memory Architecture
- Attention as associative memory: KV cache stores command pattern associations
- QLoRA adapters as task-specific memory augmentation (~20M params / 2.2%)
- ChatML structured prompting as memory addressing mechanism
- Response-only masking focuses memory on command generation

### 3.5 GGUF Export
- q4_k_m (~500MB) for RPi/edge
- q8_0 (~900MB) for Mac/desktop

## 4. Experiments (~0.75 page)

### Metrics
1. Character-level BLEU (charBLEU) — NLC2CMD standard
2. Template Accuracy — structural match ignoring args
3. Exact Match — strict string equality
4. Execution Accuracy — sandboxed execution (50 prompts, IBM methodology)

### Baselines

| Model | Params | Access |
|-------|--------|--------|
| GPT-4o | ~1.8T | API (0-shot) |
| Claude 3.5 Sonnet | Unknown | API (0-shot) |
| CodeT5-base | 220M | Open |
| Qwen3.5-0.8B (no FT) | 0.9B | Open (ablation) |
| **NL2Shell 0.8B** | **0.9B** | **Open** |

### Ablations
- Without macOS synthetic data
- Without train_on_responses_only
- Without sequence packing

## 5. Results (~0.75 page)

### 5.1 Main Results (NL2Bash test, n=606)
[Table: charBLEU / Template Acc / EM — fill after training]

### 5.2 macOS Domain Adaptation (n=40)
[Table: w/ and w/o macOS augmentation — fill after training]

### 5.3 Edge Deployment Benchmarks

| Device | Tokens/sec | TTFT | Model fits? |
|--------|-----------|------|-------------|
| RPi 5 (8GB) | [measure] | [measure] | Yes |
| Apple M2 (16GB) | [measure] | [measure] | Yes |

### 5.4 Qualitative Examples
[4-6 NL -> shell pairs with correct/incorrect labels]

## 6. Discussion (~0.5 page)
- Strengths: single-utility commands, pipe chains, macOS brew/lsof
- Failures: multi-step unusual combos, unseen numeric args, PowerShell OOS
- QLoRA efficiency: <$2 training cost, ~20M trainable params
- Limitations: no user study, BLEU insufficient alone, no safety eval

## 7. Conclusion (~0.25 page)
- Sub-1B model achieves competitive NL2Bash accuracy, runs offline on edge
- Training cost under $2, inference footprint under 500MB
- Future: larger datasets (40k), RLEF, PowerShell, terminal plugin

---

## Figures & Tables Checklist

| # | Type | Content | Section |
|---|------|---------|---------|
| Fig 1 | Diagram | Architecture: Qwen3.5 + QLoRA + ChatML flow | 3 |
| Fig 2 | Plot | Training loss curves (3 epochs) | 4 |
| Fig 3 | Examples | NL -> shell qualitative results | 5 |
| Fig 4 | Bar chart | Edge benchmark tokens/sec | 5.3 |
| Table 1 | Dataset | Composition and splits | 3.2 |
| Table 2 | Config | QLoRA hyperparameters | 3.3 |
| Table 3 | Results | Main benchmark scores | 5.1 |
| Table 4 | Ablation | macOS augmentation effect | 5.2 |
| Table 5 | Deploy | Edge device performance | 5.3 |

---

## Key References
1. Lin et al. (2018) — Tellina / NL2Bash (arXiv:1802.08979)
2. Hochstetter et al. (2020) — NLC2CMD NeurIPS competition
3. Westenfelder & Finn (2025) — LLM-Supported NL2Bash (arXiv:2502.06858, NAACL)
4. IBM (2024) — NL2Bash-EAbench (arXiv:2405.06807)
5. Dettmers et al. (2023) — QLoRA (arXiv:2305.14314)
6. Hu et al. (2021) — LoRA (arXiv:2106.09685)
7. Qwen Team (2025) — Qwen3.5 technical report
8. Evtikhiev et al. (2023) — Out of the BLEU (arXiv:2208.03133)

---

## Novelty Claims (REVISED — prior art exists)
1. **First hybrid DeltaNet architecture for NL2Bash** — Qwen3.5 (Feb 2026) uses 75% Gated DeltaNet + 25% softmax; all prior work uses dense transformers (Qwen2.5, Llama, Gemma, T5)
2. **Neural memory framing** — first to analyze NL2Bash through three-tier memory lens (parametric base + QLoRA delta + ChatML addressing); supported by Geva 2021, Titans 2025
3. **Edge deployment benchmarks** — first RPi 5 / Apple M-series latency measurements for NL2Bash GGUF models
4. **macOS domain adaptation** — 40 synthetic pairs for platform-specific shell commands (brew, launchctl, lsof, diskutil)
5. **Accuracy over prior 0.5B** — Westenfelder's Qwen2.5-Coder-0.5B scored 0.27 on IC-ALFA; target > 0.40 with Qwen3.5-0.8B

NOTE: westenfelder/Qwen2.5-Coder-0.5B-NL2SH (NAACL 2025), BashGemma-270M (Zenodo Dec 2025), and BashGPTNeo-125M exist. See research-prior-art.md for full list.

## Writing Tools
- Overleaf (ACL template)
- SciSpace (related work search)
- OpenAI Prism (citation formatting)
- Paperpal (grammar/tone check)
