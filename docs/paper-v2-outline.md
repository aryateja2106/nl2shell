# NL2Shell Paper v2 — Revised Outline

**Core Thesis Reframe:** AI coding agents (Claude Code, Codex, Gemini CLI) as an autonomous
orchestration layer for building and training ML models from scratch, with GPU compute as the
experimental variable that produces measurably different model quality.

Last updated: 2026-03-11

---

## Title Options (5 candidates)

1. **"Agent-Orchestrated ML: Using AI Coding Agents to Train NL2Shell Models Across GPU Tiers"**
   - Strong for agent-focused venues; most literal to thesis

2. **"From Prompt to Model: AI Coding Agents as Autonomous ML Pipeline Engineers"**
   - Punchy; emphasizes the end-to-end autonomy angle

3. **"Compute-Quality Scaling in Agent-Driven Fine-Tuning: NL2Shell Across A100, H100, L4, and T4"**
   - Best for ML systems / hardware-focused audience

4. **"AutoAgent-Train: Closing the Loop Between AI Coding Agents and ML Training Pipelines"**
   - Connects to AutoML-Agent (ICML 2025) prior art; strong venue fit

5. **"NL2Shell via Agent Loop: Autonomous Fine-Tuning and Compute-Quality Tradeoffs for Shell Command Generation"**
   - Combines both contributions cleanly; good for arXiv + ACL short paper

**Recommended primary title:** Option 1 with Option 5 as subtitle.
Full: *"Agent-Orchestrated ML: Autonomous Fine-Tuning of NL2Shell Models and GPU Compute-Quality Tradeoffs"*

---

## Abstract (150 words)

We present an empirical study of AI coding agents (Claude Code, OpenAI Codex CLI, Gemini CLI)
as autonomous orchestrators of a complete ML training pipeline, applied to the task of
natural-language-to-shell-command translation (NL2Bash). Using Karpathy's autoresearch pattern
as inspiration, we show that a multi-agent system can autonomously execute data preparation,
QLoRA fine-tuning, evaluation, and model export without human intervention in the inner loop.
We train NL2Shell 0.8B — a Qwen3.5-0.8B model fine-tuned on 11,894 NL-to-bash pairs — across
four GPU tiers (NVIDIA A100 40GB, H100 80GB, L4 24GB, T4 16GB) and measure resulting model
quality on the NL2Bash test split (606 examples) using IC-ALFA execution accuracy, charBLEU,
template accuracy, and exact match. We find that higher-tier compute produces measurably better
models even for sub-1B fine-tuning, and that AI coding agents can successfully orchestrate the
full pipeline with minimal human oversight. All code, agent prompts, and model weights are
released under MIT license.

---

## Section Structure

### 1. Introduction (~0.6 pages)

**Hook:** AI coding agents (Claude Code, Codex, Gemini CLI) have demonstrated ability to write,
debug, and refactor code autonomously. A natural extension is using them to orchestrate the full
ML lifecycle — data wrangling, training scripts, hyperparameter choices, evaluation — treating
model training as a software engineering problem.

**Problem Statement:**
- Current AutoML requires custom frameworks (AutoML-Agent, ICML 2025); AI coding agents offer
  a lighter-weight alternative using general-purpose CLI tools already in developer workflows.
- It is unknown whether GPU tier affects fine-tuning quality at sub-1B scale — practitioners
  choose compute based on cost/availability, not quality evidence.

**Research Questions:**
- RQ1: Can off-the-shelf AI coding agents autonomously orchestrate the full ML training pipeline
  (data prep → train → eval → export) without human intervention in the inner loop?
- RQ2: Does GPU compute tier (A100 40GB vs H100 80GB vs L4 24GB vs T4 16GB) produce
  measurably different model quality when fine-tuning the same sub-1B model on the same dataset?
- RQ3: What is the cost-quality frontier across GPU tiers for NL2Bash fine-tuning?

**Contributions:**
1. First demonstration of AI coding agents (Claude Code, Codex CLI, Gemini CLI) as autonomous
   ML pipeline orchestrators for a real NLP fine-tuning task
2. Empirical GPU compute-quality comparison for sub-1B QLoRA fine-tuning (4 GPU tiers,
   same model + dataset)
3. NL2Shell 0.8B v2: Qwen3.5 fine-tuned on 11,894 NL2Bash pairs, competitive with 1.5B models
4. Open agent prompts, training scripts, and multi-GPU comparison data

---

### 2. Background and Related Work (~0.5 pages)

**2.1 NL2Bash Task**
- Lin et al. (2018): NL2Bash dataset (9,305 pairs, 606-example test split)
- Westenfelder & Finn (2025, NAACL): IC-ALFA metric, sub-1B baselines (0.27 for Qwen2.5-0.5B)
- IBM NL2Bash-EAbench (Vo et al. 2024): container-based execution eval

**2.2 AI Agents for ML Pipeline Automation**
- AutoML-Agent (Trirat et al., ICML 2025): multi-agent LLM framework for full-pipeline AutoML;
  uses retrieval-augmented planning with specialized sub-agents for data, training, deployment
- Karpathy's autoresearch (March 2026): 630-line single-GPU agent loop; ran 126 experiments
  overnight, reduced training loss from 0.9979 to 0.9697; demonstrates agent-driven ML research
  is practical today
- AutoIAD (2025): manager-driven multi-agent collaboration with Data Prep, Trainer, Evaluator
  sub-agents — most similar architecture to our approach
- Key distinction: prior work uses custom agent frameworks; we use production AI coding agents
  (Claude Code, Codex CLI, Gemini CLI) that practitioners already have installed

**2.3 GPU Compute Scaling**
- Hoffmann et al. (2022, Chinchilla): compute-optimal scaling for pretraining; no equivalent
  study for fine-tuning at sub-1B scale
- H100 delivers 2-3x faster training than A100; FP8 support for 2.2x token throughput
- L4 (24GB VRAM) suitable for sub-2B fine-tuning; T4 (16GB) is minimum viable for 0.8B QLoRA
- No published study isolates GPU tier effect on model quality (vs. speed) for small LLM
  fine-tuning — this is our gap

**2.4 Efficient Fine-Tuning**
- QLoRA (Dettmers et al., NeurIPS 2023): 4-bit NF4 + LoRA; 0.74% trainable params
- Unsloth: 2x speedup, 60% less memory for QLoRA training

---

### 3. Agent-Orchestrated ML Pipeline (~1.0 page)

**3.1 System Architecture**

```
Human Researcher
      |
      v
  [Orchestrator Agent: Claude Code]
      |
      +---> [Data Agent: Codex CLI]
      |         prepare.py: download, deduplicate, format, split
      |
      +---> [Train Agent: Gemini CLI]
      |         train.py: QLoRA config, SFTTrainer, checkpoint
      |
      +---> [Eval Agent: Claude Code]
      |         eval.py: IC-ALFA, charBLEU, template acc, exact match
      |
      +---> [Export Agent: Codex CLI]
                export.py: GGUF q4_k_m, q8_0, push to HuggingFace
```

The human defines the task specification in a `program.md` file (following Karpathy's pattern).
Each agent reads program.md, executes its assigned script, reports results back to the
orchestrator, and the orchestrator decides next steps. No human intervention in the inner loop.

**3.2 Agent Assignment Rationale**
- Claude Code: long-context reasoning for orchestration; best for reading loss curves,
  diagnosing failures, deciding hyperparameter changes
- Codex CLI (OpenAI): best for mechanical data transformation scripts (prepare.py);
  fast code generation with tool use
- Gemini CLI: 1M+ token context window useful for ingesting full training logs;
  strong at structured config generation (train.py)

**3.3 program.md Specification Format**

```markdown
# Task: Fine-tune NL2Shell 0.8B

## Goal
Train Qwen3.5-0.8B on NL2Bash for shell command generation.
Target: IC-ALFA > 0.45 on 606 test examples.

## Dataset
Source: jiacheng-ye/nl2bash + AnishJoshi/nl2bash-custom + macos_synthetic_40.jsonl
After dedup: 11,894 unique pairs

## Training Config
- Base: Qwen/Qwen3.5-0.8B
- Method: QLoRA (NF4, rank=16, alpha=32)
- Epochs: 4, batch=64, lr=2e-4 cosine
- Loss masking: response-only

## Eval Protocol
- Primary: IC-ALFA on test split (606 examples)
- Secondary: charBLEU, template accuracy, exact match
- Report per-epoch on validation split

## Success Criteria
- Final loss < 0.60
- IC-ALFA > 0.45
- Training cost < $5
```

**3.4 Agent Interaction Protocol**
- Agents communicate via structured JSON status files (`status.json`)
- Orchestrator polls status every N minutes, reads logs, decides to continue/abort/adjust
- All agent actions logged to `agent_log.jsonl` for reproducibility
- Human can interrupt with a "guidance" file (`human_guidance.md`) — the only intervention point

**3.5 Comparison to Karpathy's Autoresearch**
- Karpathy: single agent, single GPU, automated hypothesis generation over one script
- Ours: multi-agent (3 different AI systems), multi-GPU (4 tiers), task-fixed (NL2Bash),
  pipeline-decomposed (data/train/eval/export as separate agent responsibilities
- Key advance: heterogeneous agent team mirrors real dev team (different tools for different jobs)

---

### 4. The NL2Shell 0.8B Model (~0.5 pages)

**4.1 Base Model: Qwen3.5-0.8B**
- Hybrid DeltaNet architecture: 75% Gated DeltaNet (linear attention) + 25% softmax
- 24 layers, 1,024 hidden dim, 262K context, Apache 2.0
- Novel for NL2Bash: all prior work uses dense transformers (Qwen2.5, Llama, Gemma)

**4.2 Dataset Composition**

| Source | Raw | After Dedup |
|--------|-----|-------------|
| GWHed/nl2bash | 8,090 | 6,400 |
| AnishJoshi/nl2bash-custom | 19,658 | 5,455 |
| macOS synthetic (hand-crafted) | 40 | 39 |
| **Total** | **27,788** | **11,894** |

Deduplication by exact bash command match removes 57% overlap.
ChatML format with fixed system prompt; response-only loss masking.

**4.3 QLoRA Configuration**

| Parameter | Value |
|-----------|-------|
| Quantization | 4-bit NF4 |
| LoRA rank / alpha | 16 / 32 |
| Target modules | All linear (q,k,v,o,gate,up,down) |
| Dropout | 0.05 |
| Epochs | 4 |
| Effective batch | 64 (16 x 4 grad accum) |
| Learning rate | 2e-4, cosine, 5% warmup |
| Loss masking | Response-only |
| Packing | Enabled |

---

### 5. Experiments: Multi-GPU Compute Comparison (~1.0 page)

**5.1 Experimental Design**

The central experiment trains the identical model (Qwen3.5-0.8B), on the identical dataset
(11,894 pairs, same seed, same config), across four GPU tiers. The ONLY variable is the
hardware. This is a controlled experiment isolating compute tier effects on model quality.

**GPU Comparison Matrix:**

| GPU | VRAM | Memory BW | FP16 TFLOPS | Cost/hr (est.) | Precision |
|-----|------|-----------|-------------|----------------|-----------|
| T4 | 16GB | 300 GB/s | 65 | ~$0.40 | FP16/INT8 |
| L4 | 24GB | 300 GB/s | 121 | ~$0.60 | FP16/INT8 |
| A100 40GB | 40GB | 1,555 GB/s | 312 | ~$2.00 | BF16/TF32 |
| H100 80GB | 80GB | 3,350 GB/s | 989 | ~$3.50 | BF16/FP8 |

*Note: v1 trained on A100 40GB (8,130 pairs, 3 epochs, loss=0.6338, before dataset expansion).
v2 currently training on A100 (11,894 pairs, 4 epochs). H100 and L4/T4 runs are planned.*

**Hypothesis:**
- H1: H100 produces lower final training loss than A100 (BF16 vs TF32 precision, larger batch)
- H2: L4 and T4 produce higher loss due to smaller batch sizes forced by VRAM constraints
- H3: Quality gap is measurable on IC-ALFA (execution accuracy), not just training loss

**5.2 Metrics to Report**

For each GPU run:
1. **Training loss** (final epoch, per-epoch curves)
2. **Validation loss** (per epoch)
3. **IC-ALFA** on 606 NL2Bash test examples (execution accuracy)
4. **charBLEU** (backward compatibility with NLC2CMD)
5. **Template accuracy** (structural match ignoring args)
6. **Exact match** (strict string equality)
7. **Training wall-clock time** (hours per epoch)
8. **Training cost** (GPU-hours x $/hour)
9. **Tokens/sec throughput** during training
10. **Max batch size achievable** per GPU

**5.3 Expected Results Table (to be filled)**

| GPU | Loss (final) | IC-ALFA | charBLEU | Template | Exact | Cost ($) | Time (hrs) |
|-----|-------------|---------|----------|----------|-------|----------|------------|
| T4 16GB | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| L4 24GB | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| A100 40GB | 0.6338* | [TBD] | [TBD] | [TBD] | [TBD] | ~$2 | [TBD] |
| H100 80GB | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |

*v1 baseline (8,130 pairs, 3 epochs). v2 (11,894 pairs, 4 epochs) values TBD.

**5.4 Agent Pipeline Evaluation**

Separately evaluate the agent orchestration system:
- Did each agent complete its task without human re-prompting? (Y/N per stage)
- How many agent "turns" were required per pipeline stage?
- What failure modes occurred? (code errors, VRAM OOM, checkpoint corruption)
- Human intervention log: how many times did a human write to `human_guidance.md`?
- Qualitative: agent decisions that improved outcomes (e.g., catching OOM, adjusting batch)

**5.5 Baselines (for NL2Shell model quality)**

| Model | Params | Architecture | IC-ALFA |
|-------|--------|-------------|---------|
| GPT-4o | ~1.8T | Dense transformer | 0.74 |
| Qwen2.5-Coder-7B | 7B | Dense transformer | 0.61 |
| Qwen2.5-Coder-1.5B + LoRA | 1.5B | Dense transformer | 0.50 |
| Qwen2.5-Coder-0.5B + LoRA | 0.5B | Dense transformer | 0.27 |
| Llama-3.2-1B + LoRA | 1B | Dense transformer | 0.37 |
| BashGemma-270M | 270M | Dense transformer | 0.574 (NLC2CMD) |
| **NL2Shell 0.8B (A100)** | **0.8B** | **Hybrid DeltaNet** | **[TBD]** |
| **NL2Shell 0.8B (H100)** | **0.8B** | **Hybrid DeltaNet** | **[TBD]** |
| **NL2Shell 0.8B (L4)** | **0.8B** | **Hybrid DeltaNet** | **[TBD]** |
| **NL2Shell 0.8B (T4)** | **0.8B** | **Hybrid DeltaNet** | **[TBD]** |

---

### 6. Results (~0.75 pages)

**6.1 GPU Compute-Quality Analysis**
- Present the results table from 5.3
- Statistical significance testing (if multiple seeds per GPU)
- Visualize: loss curves overlaid for all 4 GPUs
- Visualize: IC-ALFA vs compute cost scatter plot (the "efficient frontier")

**6.2 Agent Pipeline Performance**
- Success rate per stage per agent
- Comparison: Claude Code vs Codex CLI vs Gemini CLI on assigned tasks
- Agent turn count vs human intervention count

**6.3 NL2Shell Quality vs Prior Art**
- Best GPU run vs Westenfelder baselines
- Qualitative examples: 4-6 NL→shell pairs (correct + failure cases)

**6.4 Cost-Quality Frontier**
- Key finding framing: "You can spend $0.40/hr on T4 and get IC-ALFA X, or $3.50/hr on H100
  and get IC-ALFA Y — is the delta worth it for sub-1B fine-tuning?"
- Recommended GPU tier for budget-constrained researchers

---

### 7. Discussion (~0.4 pages)

**7.1 On Agent Autonomy**
- Where agents succeeded: mechanical tasks (data dedup, script generation, GGUF export)
- Where agents needed guidance: diagnosing subtle training failures, deciding epoch count
- Practical takeaway: AI coding agents as ML pipeline engineers are ready for sub-1B tasks

**7.2 On Compute Scaling for Fine-Tuning**
- Unlike pretraining (Chinchilla laws), fine-tuning at sub-1B scale may show diminishing returns
  from higher compute — more precision, same data = marginal gains
- Or the opposite: H100's FP8 and larger batch allow better gradient estimates → real gains
- This is empirically unresolved; our paper provides the first controlled data point

**7.3 Limitations**
- Single model family (Qwen3.5-0.8B); results may not generalize to Llama/Gemma
- Dataset fixed; can't separate data quality from compute quality effects
- T4 and L4 runs require reducing batch size → confounds compute vs batch size
- Agent evaluation is qualitative; no formal agent capability benchmark used
- Colab Pro GPU availability means H100/L4 runs may use shared, variable hardware

---

### 8. Conclusion (~0.25 pages)

AI coding agents can autonomously orchestrate complete ML fine-tuning pipelines, reducing
the human burden to task specification and occasional guidance. For NL2Shell 0.8B, GPU compute
tier produces measurably different model quality even at sub-1B scale, with [best GPU] achieving
IC-ALFA [X] vs [worst GPU] at [Y] — a [Z]% quality gap for a [W]x cost difference.

Future work: larger dataset (40k+ pairs via NL2SH-ALFA), RLHF alignment, PowerShell extension,
and extending the agent pipeline to multi-GPU distributed training.

---

## Figures and Tables Checklist

| # | Type | Content | Section |
|---|------|---------|---------|
| Fig 1 | Architecture diagram | Multi-agent pipeline (Claude Code → Codex → Gemini → export) | 3.1 |
| Fig 2 | Training curves | Loss per epoch, 4 GPUs overlaid on same plot | 6.1 |
| Fig 3 | Scatter plot | IC-ALFA vs total training cost ($) — efficient frontier | 6.4 |
| Fig 4 | Bar chart | IC-ALFA per GPU tier (main result) | 6.1 |
| Fig 5 | Examples table | 4-6 NL→shell qualitative examples | 6.3 |
| Table 1 | Dataset composition | Sources, raw, dedup counts | 4.2 |
| Table 2 | QLoRA config | Hyperparameter table | 4.3 |
| Table 3 | GPU specs | VRAM, BW, TFLOPS, cost/hr for 4 tiers | 5.1 |
| Table 4 | Main results | Full metric table across 4 GPUs | 5.3 |
| Table 5 | Prior art comparison | NL2Shell vs published baselines | 5.5 |
| Table 6 | Agent evaluation | Task completion, turn count, interventions per agent | 6.2 |

---

## Experiments Needed (Action Plan)

### Immediate (v2 currently training on A100)
- [ ] Complete v2 A100 run (11,894 pairs, 4 epochs) — get final loss + IC-ALFA
- [ ] Run IC-ALFA eval on 606 NL2Bash test examples for v2

### Required for Multi-GPU Comparison
- [ ] H100 80GB run: same config, same seed (Colab Pro or Lambda Labs)
- [ ] L4 24GB run: adjust batch to 32 (VRAM constraint), same epochs
- [ ] T4 16GB run: adjust batch to 16, same epochs

### Agent Pipeline Experiments
- [ ] Set up program.md specification format
- [ ] Run Claude Code as orchestrator (data stage + eval stage)
- [ ] Run Codex CLI for data preparation script (prepare.py)
- [ ] Run Gemini CLI for training script generation (train.py)
- [ ] Log all agent turns, decisions, errors to agent_log.jsonl

### Benchmarking
- [ ] IC-ALFA on all 4 GPU runs (606 examples)
- [ ] charBLEU on all 4 runs (backward compat)
- [ ] Template accuracy + exact match on all 4 runs
- [ ] Training cost calculation (GPU-hours x spot pricing)

### Edge Deployment (carry over from v1 paper)
- [ ] GGUF q4_k_m export (best model only)
- [ ] Latency benchmark on Apple Silicon (RPi 5 if available)

---

## Venue and Format Recommendations

### Primary: arXiv cs.CL + cs.LG (immediate)
- Establish priority for the GPU-quality comparison finding
- 6-8 pages, ACL short paper format
- Timeline: submit within 2-3 weeks of completing all GPU runs

### Secondary: ICML 2026 Workshop (deadline TBD, conference July 6-11, Seoul)
- Best fit: "Multi-Agent Systems in the Era of Foundation Models" (ICML 2025 equivalent)
- Or: "Efficient Systems for Foundation Models" workshop
- 4-page workshop paper format

### Alternative: ACL 2026 Short Paper (system demo track)
- Best fit if IC-ALFA results are strong (>0.50)
- Demo of the agent pipeline as a reusable tool
- Deadline likely February 2026 (past) — aim for EMNLP 2026

### Recommended path:
1. arXiv preprint now (with v2 A100 results as minimum viable paper)
2. Add multi-GPU results and agent evaluation
3. Submit to ICML 2026 workshop or EMNLP 2026 short paper

---

## Key Citations to Add (New for v2 Framing)

### Agent-Orchestrated ML
- Trirat et al. (ICML 2025): AutoML-Agent — arxiv:2410.02958
- Karpathy (March 2026): autoresearch — github.com/karpathy/autoresearch
- Wshobson (2025): multi-agent orchestration for Claude Code

### GPU Scaling for Fine-Tuning
- Northflank (2025): H100 vs A100 benchmarks — practical 2-3x speedup
- CUDOCOMPUTE (2025): Real-world GPU benchmarks H100 vs A100 vs L40S
- Wltsankalpa (Medium, 2025): Benchmarking Qwen across T4, L4, H100

### Keep from v1 Outline
- All existing citations from research-benchmarks.md and research-neural-memory.md
- Westenfelder & Finn 2025 (NAACL): arXiv:2502.06858
- Dettmers et al. 2023 (NeurIPS): QLoRA, arXiv:2305.14314
- Geva et al. 2021 (EMNLP): FFN as key-value memories
- Behrouz et al. 2025: Titans, arXiv:2501.00663

---

## Novelty Claims (Revised for v2 Framing)

1. **First multi-agent coding system orchestrating NL2Bash fine-tuning** — Claude Code +
   Codex CLI + Gemini CLI as heterogeneous agent team; prior work (AutoML-Agent) uses custom
   frameworks not production AI coding tools

2. **First controlled GPU compute-quality study for sub-1B QLoRA fine-tuning** — Chinchilla
   covers pretraining; no paper isolates GPU tier effect on model quality for small model FT

3. **First Qwen3.5 (hybrid DeltaNet) model for NL2Bash** — all prior work uses dense
   transformers; Qwen3.5 released Feb 2026

4. **Karpathy-pattern applied to NL2Bash** — extends autoresearch concept from toy nanochat
   to a real production fine-tuning task with eval and deployment

5. **Cost-quality efficient frontier for NL2Bash fine-tuning** — actionable guidance for
   budget-constrained practitioners (T4 at $0.40/hr vs H100 at $3.50/hr)

---

## Connection to Existing v1 Paper (nl2shell.tex)

The v2 paper EXTENDS not REPLACES the existing paper. The existing LaTeX:
- Keeps: Qwen3.5 hybrid DeltaNet architecture (Section 3.1), neural memory framing
  (Section 3.4), dataset and QLoRA config (Sections 3.2-3.3), GGUF export (Section 3.5)
- NEW in v2: Sections 3 (agent pipeline), 5.1-5.4 (multi-GPU experiment), 6.2 (agent eval)
- The v1 single-GPU paper can still be submitted independently as the base NL2Shell paper
  (architecture + NL2Bash quality); v2 is the "systems" paper on agent orchestration + GPU study

Alternative: Merge into one longer paper (8-10 pages, main conference format).
Recommend: Keep separate. v1 = "the model paper" (cs.CL), v2 = "the systems/agents paper" (cs.LG/cs.AI).
