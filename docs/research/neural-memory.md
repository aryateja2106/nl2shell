# Neural Memory Architectures — Research Notes for NL2Shell Paper

## Qwen3.5-0.8B Architecture (KEY FINDING)

Qwen3.5 (Feb 2026) is a **hybrid attention architecture**, NOT a simple Qwen2.5 increment:

| Parameter | Value |
|-----------|-------|
| Parameters | 0.8B |
| Layers | 24 |
| Hidden dim | 1,024 |
| Vocab size | 248,320 |
| Context | 262,144 (256K) |
| FFN intermediate | 3,584 |

**Hybrid layer layout:** `6 x (3 x (Gated DeltaNet -> FFN) + 1 x (Gated Attention -> FFN))`
- 75% Gated DeltaNet (linear attention, O(1) per token)
- 25% full softmax attention (global retrieval)

Gated DeltaNet: combines Mamba2 gated decay + delta rule error-correcting memory + exponential gating + causal Conv1D. Hidden state is a continuously updated associative memory.

## Three-Tier Neural Memory Framing

### 1. Parametric Base Memory (frozen Qwen3.5 weights)
- FFN layers are key-value memories (Geva et al., EMNLP 2021)
- First matrix W1 = keys (correlate with input patterns)
- Second matrix W2 = values (induce output distributions)
- DeltaNet layers: compressed associative memory in O(1)
- Full-attention layers: precise global retrieval over 256K context

### 2. Domain-Specific Delta Memory (QLoRA adapter)
- LoRA adds: W_new = W_frozen + A * B
- Under FFN-as-memory: injects new key-value associations
- Keys learn to activate on NL descriptions of shell operations
- Values learn to emit correct shell command syntax
- 4-bit NF4 compresses base memory; full-precision adapters write new memories
- Rank r controls number of independent memory dimensions

### 3. Context-Addressing (ChatML working memory)
- Role tokens (`<|im_start|>system/user/assistant`) = high-salience retrieval cues
- System prompt gates which parametric memories are active
- Suppresses non-shell generation; amplifies command-generation memories
- `<|im_start|>assistant` = retrieval trigger for autoregressive generation

## Key Academic Support

### Foundational
- **Geva et al. (EMNLP 2021):** "Transformer FFN Layers Are Key-Value Memories" — foundational
- **Geva et al. (EMNLP 2022):** FFN layers build predictions by promoting/inhibiting tokens
- **Dai et al. (ACL 2022):** "Knowledge Neurons in Pretrained Transformers"
- **Hu et al. (ICLR 2022):** LoRA

### 2023-2024
- **Dettmers et al. (NeurIPS 2023):** QLoRA — NF4 quantization + LoRA
- **LoRA-FA (2023):** Frozen-A for reduced activation memory
- **Packer et al. (2023):** MemGPT — OS-inspired hierarchical memory

### 2025-2026
- **Titans (Behrouz et al., Google, 2025):** Three-tier memory taxonomy — short-term (attention), long-term (test-time learning), persistent (task parameters). LoRA = persistent memory.
- **Wang et al. (ICLR 2025):** "Generalization vs. Memorization" — shell commands are knowledge-intensive, memorization-dominant task
- **MeMo (Zanzotto et al., ACL Findings 2025):** "Memorization precedes learning" — explicit memorization is prerequisite to generalization
- **Semmler et al. (NAACL 2025):** NL2SH-ALFA — Llama-1B: 12% baseline -> 37% with interventions; Qwen better aligned for shell
- **Memory-Augmented Transformers Survey (2025):** 100+ paper taxonomy (arxiv 2508.10824)
- **Qwen3.5 (Feb 2026):** Gated DeltaNet hybrid (arxiv 2412.06464 for DeltaNet math)

## Why This Matters for NL2Shell

1. Shell command generation is **memorization-dominant** (Wang et al.) — fine-tuning maximizes pattern coverage
2. Small models benefit most from explicit fine-tuning (NL2SH-ALFA)
3. QLoRA adapters are literally "persistent memory modules" in Titans' taxonomy
4. DeltaNet layers provide O(1) compressed memory ideal for structured retrieval
5. ChatML role tokens are learned memory addressing handles

## Paper Framing

"NL2Shell 0.8B employs a three-layer neural memory architecture:
(1) parametric base memory in Qwen3.5's hybrid DeltaNet-attention layers storing general linguistic and shell knowledge,
(2) domain-specific delta memory via QLoRA adapters injecting NL2Bash associations,
(3) structured memory addressing via ChatML role tokens directing retrieval toward shell command generation."

## Citation List
- Geva et al. 2021 (EMNLP): arxiv 2012.14913
- Geva et al. 2022 (EMNLP): FFN prediction building
- Dai et al. 2022 (ACL): Knowledge neurons
- Hu et al. 2022 (ICLR): LoRA, arxiv 2106.09685
- Dettmers et al. 2023 (NeurIPS): QLoRA, arxiv 2305.14314
- Behrouz et al. 2025: Titans, arxiv 2501.00663
- Wang et al. 2025 (ICLR): Memorization vs generalization, arxiv 2407.14985
- Zanzotto et al. 2025 (ACL Findings): MeMo, arxiv 2502.12851
- Semmler et al. 2025 (NAACL): NL2SH-ALFA, arxiv 2502.06858
- Memory survey 2025: arxiv 2508.10824
- DeltaNet 2024: arxiv 2412.06464
