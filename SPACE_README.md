---
title: NL2Shell — Natural Language to Shell Commands
emoji: 💻
colorFrom: green
colorTo: gray
sdk: gradio
sdk_version: 5.29.0
python_version: "3.12"
app_file: app.py
pinned: false
license: mit
models:
  - AryaYT/nl2shell-0.8b
datasets:
  - jiacheng-ye/nl2bash
tags:
  - text-generation
  - shell
  - bash
  - command-line
  - nl2bash
  - qwen
  - qlora
  - code
short_description: Convert plain English into shell commands with a 0.8B model
---

# NL2Shell — Natural Language to Shell Commands

Demo for [AryaYT/nl2shell-0.8b](https://huggingface.co/AryaYT/nl2shell-0.8b), an 800M-parameter model
that converts plain English into executable shell commands.

Type a description like:

> *find all Python files modified in the last 24 hours*

and get back:

```bash
find . -name '*.py' -mtime -1
```

No markdown. No explanation. Just the command.

---

## Hardware

This Space runs on the **free CPU tier** by default (16 GB RAM, 2 vCPU). Generation takes 5–20 seconds
on CPU depending on output length. For faster inference:

- **Duplicate this Space** and select a GPU tier (T4 ~$0.40/hr on HF)
- **Run locally** via Ollama (instant, no GPU required on M-series Mac):
  ```bash
  ollama run hf.co/AryaYT/nl2shell-0.8b
  ```

---

## Model Details

| Property | Value |
|---|---|
| Base model | [Qwen/Qwen3.5-0.8B](https://huggingface.co/Qwen/Qwen3.5-0.8B) |
| Fine-tuning method | QLoRA (4-bit, rank 16, alpha 32) |
| Training data | [NL2Bash](https://huggingface.co/datasets/jiacheng-ye/nl2bash) + 40 macOS synthetic pairs |
| Prompt format | ChatML |
| Parameters | ~800M |
| GGUF sizes | q4_k_m ~400 MB, q8_0 ~650 MB |
| License | MIT |

---

## Input Format (ChatML)

The model expects this exact prompt structure at inference time:

```
<|im_start|>system
You are an expert shell programmer. Given a natural language request, output ONLY the corresponding shell command. No explanations.<|im_end|>
<|im_start|>user
{your natural language request}<|im_end|>
<|im_start|>assistant
```

The app handles this automatically. If you call the model directly, use this template.

---

## Local Usage

### Ollama (recommended)

```bash
# Pull and run — downloads q4_k_m GGUF (~400 MB)
ollama run hf.co/AryaYT/nl2shell-0.8b

# One-shot from the command line
ollama run hf.co/AryaYT/nl2shell-0.8b "show disk usage of each subdirectory"
```

Add to your shell config as a function:

```bash
nl() {
    ollama run hf.co/AryaYT/nl2shell-0.8b "$*" 2>/dev/null
}
# Usage: nl find all Python files modified today
```

### Python (transformers)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "AryaYT/nl2shell-0.8b"
SYSTEM = (
    "You are an expert shell programmer. Given a natural language request, "
    "output ONLY the corresponding shell command. No explanations."
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, device_map="auto")

def nl2shell(request: str) -> str:
    prompt = (
        f"<|im_start|>system\n{SYSTEM}<|im_end|>\n"
        f"<|im_start|>user\n{request}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=128,
        temperature=0.1,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
    )
    full = tokenizer.decode(outputs[0], skip_special_tokens=False)
    cmd = full.split("<|im_start|>assistant\n")[-1].split("<|im_end|>")[0].strip()
    return cmd

print(nl2shell("show all running Docker containers"))
# docker ps
```

---

## Safety

Shell commands can be destructive. Always review generated output before running it, especially
commands involving `rm`, `kill`, `sudo`, or network operations. This is a research demo.

---

## Source

- Model: [AryaYT/nl2shell-0.8b](https://huggingface.co/AryaYT/nl2shell-0.8b)
- Training repo: [aryateja2106/cloudagi](https://github.com/aryateja2106/cloudagi)
- Project: [CloudAGI](https://cloudagi.ai) — Agent Credit Economy
- Author: [Arya Teja](https://github.com/aryateja2106)
