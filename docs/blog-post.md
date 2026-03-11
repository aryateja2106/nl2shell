# Building NL2Shell: Fine-Tuning Qwen3.5-0.8B for Shell Command Generation

*By Arya Teja | March 2026 | [CloudAGI](https://cloudagi.ai)*

---

## What We Built

**NL2Shell 0.8B** is the first fine-tune of Qwen3.5-0.8B for natural language to shell command translation. Type "find all Python files modified today" and get `find . -name '*.py' -mtime -1`. No explanations, no fluff — just the command.

- **Model:** [AryaYT/nl2shell-0.8b](https://huggingface.co/AryaYT/nl2shell-0.8b)
- **Dataset:** [AryaYT/nl2shell-training](https://huggingface.co/datasets/AryaYT/nl2shell-training) (11,894 pairs)
- **Demo:** [Live on HuggingFace Spaces](https://huggingface.co/spaces/AryaYT/nl2shell-demo)
- **License:** MIT

## Why Qwen3.5-0.8B?

Qwen3.5-0.8B uses a **hybrid DeltaNet architecture** — 75% linear attention + 25% softmax attention across its 24 layers. This gives it:

- **Sub-1B parameter count** (859M) — fits on a Raspberry Pi with q4_k_m quantization (~400MB)
- **262K context window** — far more than needed for shell commands, but shows the architecture's capability
- **State-space-like efficiency** at inference — the linear attention layers process tokens in O(1) per step

For edge deployment (local shell assistants, IDE integrations), this is the sweet spot: small enough to run on-device, capable enough to generate accurate commands.

## The Dataset

### v1: 8,130 Pairs
- **GWHed/nl2bash** (~8,090 examples) — the classic NL2Bash benchmark dataset
- **40 macOS synthetic pairs** — hand-written commands for Homebrew, `lsof`, `fswatch`, etc.

### v2: 11,894 Deduplicated Pairs (+47%)
- Added **AnishJoshi/nl2bash-custom** (~19,658 raw rows)
- Deduplicated by bash command (keep first occurrence, GWHed has priority)
- Normalized whitespace, dropped empty/nan rows
- All formatted as ChatML with a system prompt enforcing command-only output

The v2 dataset is published at [AryaYT/nl2shell-training](https://huggingface.co/datasets/AryaYT/nl2shell-training).

## Training Setup

| Parameter | v1 | v2 |
|-----------|----|----|
| Dataset | 8,130 pairs | 11,894 pairs |
| LoRA rank / alpha | 16 / 32 | 16 / 32 |
| Epochs | 3 | 4 |
| Effective batch size | 32 | 64 |
| Warmup | 20 steps | 5% of total steps |
| Hardware | A100 40GB | A100 40GB |
| Final loss | 0.6338 | *in progress* |

**Method:** QLoRA with 4-bit NF4 quantization, targeting all linear layers (`q/k/v/o_proj`, `gate/up/down_proj`). Response-only loss masking via `train_on_responses_only` — the model only learns to predict assistant tokens, not the system prompt or user input.

**Framework:** Unsloth + TRL's SFTTrainer with packing enabled.

## Agent-Orchestrated Training

The entire pipeline — from dataset preparation to model export — was orchestrated by AI coding agents (Claude Code) managing GPU compute remotely. The workflow:

1. **Claude Code** writes and iterates on `prepare.py`, `train.py`, `benchmark.py`
2. **lecoder-cgpu** bridges to Colab Pro GPU instances (A100)
3. Claude monitors training progress, adjusts hyperparameters, handles errors
4. On completion, model is automatically exported (merged 16-bit + GGUF) and pushed to HuggingFace

This is Karpathy's "autoresearch" pattern applied to fine-tuning: the human provides direction and taste, the agent handles execution and iteration.

### Lesson: Colab Pro >> GCP Enterprise for Small Research

We initially tried GCP Colab Enterprise. All 3 GPU jobs failed — 0 GPU quota despite having $300 in credits. Colab Pro with lecoder-cgpu worked immediately with A100 access. For quick fine-tuning experiments, Colab Pro at $12/month beats GCP Enterprise every time.

## Example Outputs (v1 Model)

```
NL:  list all files in the current directory
CMD: ls -la

NL:  find all Python files larger than 1MB
CMD: find . -name "*.py" -size +1M

NL:  show the last 20 lines of a log file
CMD: tail -20 /var/log/syslog

NL:  check which process is using port 8080
CMD: lsof -i :8080

NL:  count the number of lines in all .py files recursively
CMD: find . -name "*.py" -exec wc -l {} +
```

## Try It

### Via Ollama (recommended for local use)
```bash
ollama run hf.co/AryaYT/nl2shell-0.8b
```

### Via Python
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("AryaYT/nl2shell-0.8b")
tokenizer = AutoTokenizer.from_pretrained("AryaYT/nl2shell-0.8b")

prompt = (
    "<|im_start|>system\n"
    "You are an expert shell programmer. Given a natural language request, "
    "output ONLY the corresponding shell command. No explanations.<|im_end|>\n"
    "<|im_start|>user\nfind all Python files modified today<|im_end|>\n"
    "<|im_start|>assistant\n"
)
inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=64, temperature=0.1)
print(tokenizer.decode(outputs[0], skip_special_tokens=False))
```

### Via the Live Demo
Visit [huggingface.co/spaces/AryaYT/nl2shell-demo](https://huggingface.co/spaces/AryaYT/nl2shell-demo) for an interactive Gradio interface.

## What's Next

1. **v2 model release** — currently training on 11,894 pairs with 4 epochs, expected to improve over v1
2. **Benchmark evaluation** — charBLEU, template accuracy, exact match on 606 NL2Bash test examples (baseline to beat: Qwen2.5-Coder-0.5B = 0.46 IC-ALFA)
3. **Multi-GPU experiment** — train identical model on H100, A100, L4, T4 to measure compute-quality tradeoffs
4. **Edge deployment** — GGUF q4_k_m for Raspberry Pi, q8_0 for Mac/desktop
5. **Research paper** — targeting arXiv cs.CL + EMNLP 2026 or ENLSP@NeurIPS 2026

## Links

- **Model:** [huggingface.co/AryaYT/nl2shell-0.8b](https://huggingface.co/AryaYT/nl2shell-0.8b)
- **Dataset:** [huggingface.co/datasets/AryaYT/nl2shell-training](https://huggingface.co/datasets/AryaYT/nl2shell-training)
- **Demo:** [huggingface.co/spaces/AryaYT/nl2shell-demo](https://huggingface.co/spaces/AryaYT/nl2shell-demo)
- **Code:** [github.com/aryateja2106/cloudagi](https://github.com/aryateja2106/cloudagi) (feat/nl2shell-training branch)

---

*Built by [Arya Teja](https://github.com/aryateja2106) as part of [CloudAGI](https://cloudagi.ai) — the Agent Credit Economy.*
