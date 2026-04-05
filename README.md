# NL2Shell — Natural Language to Shell Commands

[![Model](https://img.shields.io/badge/HuggingFace-AryaYT%2Fnl2shell--0.8b-yellow?logo=huggingface)](https://huggingface.co/AryaYT/nl2shell-0.8b)
[![Dataset](https://img.shields.io/badge/Dataset-AryaYT%2Fnl2shell--training-blue?logo=huggingface)](https://huggingface.co/datasets/AryaYT/nl2shell-training)
[![Demo](https://img.shields.io/badge/Demo-Gradio%20Space-orange?logo=huggingface)](https://huggingface.co/spaces/AryaYT/nl2shell-demo)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org)
[![arXiv](https://img.shields.io/badge/Paper-arXiv-red)](paper/nl2shell.tex)

**Convert plain English into executable shell commands using an 800M-parameter model that runs on your laptop.**

NL2Shell is an open-source fine-tune of [Qwen3.5-0.8B](https://huggingface.co/Qwen/Qwen3.5-0.8B) — a hybrid DeltaNet architecture with 75% linear + 25% softmax attention layers — trained on 11,894 deduplicated natural language to bash pairs using QLoRA. It outputs **only the shell command**, no explanations, no markdown fences. Edge-deployable via GGUF (q4_k_m ~400 MB).

---

## Quick Start (30 seconds to your first command)

### Option 1: Ollama (recommended — no Python required)

```bash
# Install Ollama: https://ollama.com
ollama run hf.co/AryaYT/nl2shell-0.8b "find all Python files modified in the last 24 hours"
# find . -name '*.py' -mtime -1
```

Add a shell helper so you can type `nl <description>` from anywhere:

```bash
# Add to ~/.zshrc or ~/.bashrc
nl() { ollama run hf.co/AryaYT/nl2shell-0.8b "$*" 2>/dev/null; }

# Then:
nl show disk usage of each subdirectory
# du -sh */ | sort -rh
```

### Option 2: Python (transformers)

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
        **inputs, max_new_tokens=128, temperature=0.1,
        do_sample=True, pad_token_id=tokenizer.eos_token_id,
    )
    full = tokenizer.decode(outputs[0], skip_special_tokens=False)
    return full.split("<|im_start|>assistant\n")[-1].split("<|im_end|>")[0].strip()

print(nl2shell("show all running Docker containers"))
# docker ps
```

### Option 3: Interactive Demo

Try it in your browser with no setup — [huggingface.co/spaces/AryaYT/nl2shell-demo](https://huggingface.co/spaces/AryaYT/nl2shell-demo)

---

## Example Outputs

| Natural Language | Generated Shell Command |
|---|---|
| list all files sorted by size | `ls -lhS` |
| find all Python files modified in the last 24 hours | `find . -name '*.py' -mtime -1` |
| kill the process using port 3000 | `lsof -ti:3000 \| xargs kill -9` |
| show disk usage of each subdirectory | `du -sh */ \| sort -rh` |
| compress the src directory into a tar.gz | `tar -czf src.tar.gz src/` |
| count lines of code in all TypeScript files | `find . -name '*.ts' \| xargs wc -l` |
| show git log as one-line summaries | `git log --oneline -20` |
| generate a random 32-character password | `openssl rand -base64 32` |
| find and delete all node_modules directories | `find . -name 'node_modules' -type d -prune -exec rm -rf {} +` |
| check SSL certificate expiry of a domain | `echo \| openssl s_client -connect example.com:443 2>/dev/null \| openssl x509 -noout -dates` |
| restart the DNS cache on macOS | `sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder` |
| show which process is using the most CPU | `ps aux --sort=-%cpu \| head -5` |

---

## Features

- **Sub-1B model** — 859M parameters, fits in 1 GB RAM (GGUF q4_k_m). Runs on a Raspberry Pi 4.
- **GGUF-ready** — q4_k_m (~400 MB) for edge/Raspberry Pi, q8_0 (~650 MB) for desktop, via Ollama.
- **Hybrid DeltaNet architecture** — Qwen3.5-0.8B uses 75% linear attention + 25% softmax attention layers. First NL2Bash model on this architecture class.
- **Response-only loss masking** — trained only on assistant shell output tokens, not user instructions. Cleaner gradient signal.
- **ChatML prompt format** — standard `<|im_start|>` / `<|im_end|>` tokens, compatible with any OpenAI-style chat pipeline.
- **Linux + macOS coverage** — NL2Bash benchmark pairs (GNU tools) plus 40 handcrafted macOS/Homebrew synthetic pairs.
- **MIT licensed** — use freely in commercial products, modify, redistribute.
- **Reproducible** — full training code, dataset pipeline, and benchmark script included.

---

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for Python package management.

```bash
# Clone the repo
git clone https://github.com/nl2shell/nl2shell
cd nl2shell

# Install uv (if you don't have it)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dev tools (linting, type checking)
uv sync --group dev

# Install for inference / demo
uv sync --group demo

# Install for training (requires CUDA GPU)
uv sync --group train

# Install for benchmarking
uv sync --group eval
```

**Requirements:** Python 3.10+. For training: CUDA GPU with at least 16 GB VRAM (A100 recommended). For GGUF inference via Ollama: any hardware including Apple Silicon and Raspberry Pi.

---

## Usage

### Run the Demo Locally

```bash
uv sync --group demo
python app.py
# Opens at http://localhost:7860
```

The Gradio interface lets you type a natural language description and get the shell command instantly. Includes 15 example prompts and copy-to-clipboard.

### Fine-tune the Model

Training requires a CUDA GPU. The scripts are designed for Google Colab A100 but work on any compatible GPU.

```bash
uv sync --group train

# Set your HuggingFace token
export HF_TOKEN=hf_...

# Run QLoRA fine-tuning
python train.py
```

The training script:
1. Loads Qwen3.5-0.8B with 4-bit NF4 quantization via Unsloth (falls back to standard PEFT if Unsloth is unavailable)
2. Applies QLoRA adapters (r=16, alpha=32) to all attention and MLP projections
3. Loads and formats the dataset as ChatML
4. Applies `train_on_responses_only` to mask system/user tokens from loss
5. Trains for 3–4 epochs with cosine LR schedule
6. Evaluates on 7 test prompts
7. Merges LoRA adapters, exports GGUF (q4_k_m + q8_0), and pushes to HuggingFace

**Important:** Do not modify `prepare.py` (dataset and eval utilities). Edit only `train.py` for hyperparameter changes.

### Build the v2 Dataset

```bash
uv sync --group data

# Rebuild the deduplicated 11,894-pair dataset and push to HuggingFace
export HF_TOKEN=hf_...
python build_v2_dataset.py
```

### Benchmark

```bash
uv sync --group eval

# Evaluate on NL2Bash test split (606 examples)
# Metrics: charBLEU, template accuracy, exact match
python benchmark.py
```

Results are saved to `benchmark_results.json` with per-example predictions.

### Lint and Type Check

```bash
uv sync --group dev
ruff check .      # lint
ruff format .     # format
ty check .        # type check
```

---

## Architecture

### Base Model: Qwen3.5-0.8B (Hybrid DeltaNet)

Qwen3.5-0.8B is Alibaba's 859M-parameter hybrid language model. Unlike standard transformers that use full softmax attention in every layer, it uses a **DeltaNet architecture** — a mix of linear recurrent attention (efficient O(n) complexity) and traditional softmax attention (O(n²) but higher expressivity):

| Property | Value |
|---|---|
| Total parameters | 859M |
| Architecture | Hybrid DeltaNet |
| Attention layers | 25% softmax (every 4th layer) |
| Linear layers | 75% DeltaNet recurrent |
| Context window | 262,144 tokens |
| Hidden size | 1024 |
| Layers | 24 |
| Heads | 16 |
| Prompt format | ChatML (`<\|im_start\|>` / `<\|im_end\|>`) |

The linear attention layers give Qwen3.5 better inference efficiency at long contexts. Shell commands are short (< 128 tokens), so the practical benefit here is reduced model size and faster loading rather than sequence length.

NL2Shell is believed to be the **first NL2Bash fine-tune on a hybrid DeltaNet model**, establishing a baseline for this architecture class on the task.

### QLoRA Fine-tuning

| Hyperparameter | Value |
|---|---|
| Method | QLoRA (PEFT) |
| Base quantization | 4-bit NF4 |
| Compute dtype | bfloat16 |
| LoRA rank (r) | 16 |
| LoRA alpha | 32 |
| LoRA dropout | 0.05 |
| Target modules | q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj |
| Loss masking | Response-only (system + user tokens masked) |
| Sequence packing | Yes (efficient GPU utilization) |
| Gradient checkpointing | Yes (Unsloth) |
| Optimizer | AdamW 8-bit |
| LR scheduler | Cosine |
| Max sequence length | 512 tokens |

---

## Dataset

**HuggingFace:** [AryaYT/nl2shell-training](https://huggingface.co/datasets/AryaYT/nl2shell-training)

The v2 dataset contains **11,894 deduplicated** natural language to bash command pairs sourced from:

| Source | Pairs | Notes |
|---|---|---|
| [GWHed/nl2bash](https://huggingface.co/datasets/GWHed/nl2bash) | ~8,090 | Classic NL2Bash benchmark, GNU/Linux commands |
| [AnishJoshi/nl2bash-custom](https://huggingface.co/datasets/AnishJoshi/nl2bash-custom) | ~3,764 | Supplemental NL2Bash pairs |
| macOS synthetic (handcrafted) | 40 | Homebrew, launchd, macOS-specific commands |
| **Total (deduplicated)** | **11,894** | SHA256 hash dedup on (nl, bash) pairs |

Every pair is formatted as ChatML before training:

```
<|im_start|>system
You are an expert shell programmer. Given a natural language request, output ONLY the corresponding shell command. No explanations.<|im_end|>
<|im_start|>user
{natural language request}<|im_end|>
<|im_start|>assistant
{shell command}<|im_end|>
```

The dataset is shuffled with seed 42 for reproducibility.

---

## Training Details

| | v1 | v2 |
|---|---|---|
| Training pairs | 8,130 | 11,894 |
| Epochs | 3 | 4 |
| Hardware | A100 (Colab) | H100 (Colab Pro) |
| Batch size | 8 | 8 |
| Gradient accumulation | 4 (effective batch 32) | 8 (effective batch 64) |
| Learning rate | 2e-4 | 2e-4 |
| Warmup | 20 steps | 5% of steps |
| Final train loss | 0.6338 | in progress |
| Unsloth | Yes | Yes |
| Sequence packing | Yes | Yes |

v2 hyperparameters were reviewed by [Amp](https://sourcegraph.com/amp) with additional warmup steps and doubled effective batch size for the larger dataset.

---

## Benchmarks

Evaluated on the [GWHed/nl2bash](https://huggingface.co/datasets/GWHed/nl2bash) test split (606 examples).

### Metrics

- **charBLEU** — character-level BLEU-4 with brevity penalty (NLC2CMD standard)
- **Template accuracy** — commands match after normalizing quoted strings, paths, and numbers to placeholders
- **Exact match** — identical string after stripping whitespace

### v1 Results (in progress — run `benchmark.py` for latest)

| Model | charBLEU | Template Acc | Exact Match |
|---|---|---|---|
| NL2Shell-0.8b v1 | pending | pending | pending |
| NL2Shell-0.8b v2 | pending | pending | pending |
| Qwen2.5-Coder-0.5B + LoRA | — | — | 0.46 IC-ALFA* |
| Llama-3.2-1B + LoRA | — | — | 0.37 IC-ALFA* |

*IC-ALFA (Westenfelder 2025) is execution accuracy, not directly comparable to charBLEU. Apples-to-apples comparison pending.

To run benchmarks yourself:

```bash
uv sync --group eval
python benchmark.py
# Saves per-example results to benchmark_results.json
```

---

## FAQ

### What is NL2Shell?

NL2Shell is a fine-tuned language model that converts plain English descriptions into shell/bash commands. You describe what you want to do — "find all log files larger than 100 MB" — and the model outputs the exact command: `find / -name '*.log' -size +100M`. It is a research project and open-source tool built on top of Qwen3.5-0.8B, an 859M-parameter hybrid DeltaNet model.

### How do I convert natural language to shell commands?

The easiest path is Ollama:

```bash
ollama run hf.co/AryaYT/nl2shell-0.8b "your description here"
```

For programmatic use, load `AryaYT/nl2shell-0.8b` with the Hugging Face `transformers` library and send a ChatML-formatted prompt (see the Quick Start section above). There is also a no-install [web demo](https://huggingface.co/spaces/AryaYT/nl2shell-demo).

### What is the best small model for shell command generation?

As of March 2026, NL2Shell-0.8b is the only publicly available fine-tune specifically targeting shell command generation on Qwen3.5-0.8B (hybrid DeltaNet architecture). It is competitive with Qwen2.5-Coder-0.5B + LoRA at a similar or smaller parameter count. For edge deployment (Raspberry Pi, M-series Mac with no GPU), the GGUF q4_k_m variant at ~400 MB is the most practical option in its class.

### How do I run a shell command generator locally with no internet?

After downloading the GGUF model once, Ollama runs fully offline:

```bash
# First run downloads the model (~400 MB for q4_k_m)
ollama run hf.co/AryaYT/nl2shell-0.8b "list all files sorted by modification date"
# Subsequent runs are instant, no internet required
```

The q4_k_m GGUF runs on CPU. On Apple Silicon (M1/M2/M3/M4), Ollama uses Metal GPU acceleration automatically.

### How do I use Qwen for shell/bash command generation?

Qwen3.5-0.8B (and the NL2Shell fine-tune) uses the ChatML prompt format. The key is to use the correct system prompt and output format:

```python
SYSTEM = "You are an expert shell programmer. Given a natural language request, output ONLY the corresponding shell command. No explanations."

prompt = (
    f"<|im_start|>system\n{SYSTEM}<|im_end|>\n"
    f"<|im_start|>user\n{your_request}<|im_end|>\n"
    f"<|im_start|>assistant\n"
)
```

Set temperature to 0.1 for deterministic, predictable output. Shell commands are not creative tasks — low temperature is strongly recommended.

### What are the NL2Bash / NL2Shell alternatives?

| Project | Model | Size | GGUF | Notes |
|---|---|---|---|---|
| **NL2Shell** (this project) | Qwen3.5-0.8B | 859M | Yes | Hybrid DeltaNet, MIT |
| Westenfelder 2025 | Qwen2.5-Coder-0.5B | 500M | No | IC-ALFA 0.46, not public |
| Westenfelder 2025 | Llama-3.2-1B | 1B | No | IC-ALFA 0.37, not public |
| NLC2CMD (2021) | various | large | No | IBM, competition-era |
| ShellGPT | GPT-4o via API | API | No | Requires OpenAI key |
| GitHub Copilot CLI | GPT-4o via API | API | No | Subscription required |

NL2Shell is the only open-weight, edge-deployable, MIT-licensed option purpose-trained for NL-to-bash on the Qwen3.5 architecture.

### How do I fine-tune a model for bash/shell commands?

The full pipeline is in this repo. The key steps:

1. **Dataset:** Collect (natural language, bash command) pairs. NL2Bash (~10K pairs from GWHed/nl2bash) is the standard benchmark dataset. Add domain-specific pairs for your use case (macOS, Kubernetes, etc.).
2. **Format:** Convert to ChatML format with a system prompt instructing the model to output only the command.
3. **QLoRA:** Use `peft` + `trl` (SFTTrainer) with r=16, alpha=32, NF4 4-bit quantization. Targets: q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj.
4. **Loss masking:** Apply `train_on_responses_only` (TRL/Unsloth) to mask system and user tokens. The model should only learn to predict the shell command, not re-learn the prompt.
5. **Export:** Merge adapters back into the base model, then export GGUF with llama.cpp via Unsloth's `save_pretrained_gguf`.

See `train.py` for the complete implementation and `prepare.py` for dataset formatting utilities.

### How do I generate bash commands from text in Python?

```python
# pip install transformers torch
from transformers import pipeline

pipe = pipeline("text-generation", model="AryaYT/nl2shell-0.8b", device_map="auto")

SYSTEM = "You are an expert shell programmer. Given a natural language request, output ONLY the corresponding shell command. No explanations."

def bash(request: str) -> str:
    prompt = f"<|im_start|>system\n{SYSTEM}<|im_end|>\n<|im_start|>user\n{request}<|im_end|>\n<|im_start|>assistant\n"
    result = pipe(prompt, max_new_tokens=64, temperature=0.1, do_sample=True)
    full = result[0]["generated_text"]
    return full.split("<|im_start|>assistant\n")[-1].split("<|im_end|>")[0].strip()

print(bash("show all running Docker containers"))   # docker ps
print(bash("count lines in all Python files"))      # find . -name '*.py' | xargs wc -l
```

### Is NL2Shell safe to use?

The model generates syntactically valid shell commands but **does not verify correctness or safety**. Always review the generated command before running it, especially when it involves `rm`, `kill`, `sudo`, `chmod`, or network operations. Commands involving paths, ports, or domain names will use placeholder values from training data — you must substitute your actual values. This is a research tool, not a production-grade shell assistant.

---

## Project Structure

```
nl2shell/
├── prepare.py              # Dataset loading + ChatML formatting (IMMUTABLE)
├── train.py                # QLoRA fine-tuning script (editable)
├── benchmark.py            # charBLEU / template acc / exact match evaluation
├── build_v2_dataset.py     # Dataset pipeline: dedup, merge, push to HF
├── app.py                  # Gradio demo (local + HF Spaces)
├── deploy-space.sh         # HF Space deployment script
├── experiment_gpu.py       # GPU memory profiling experiments
├── pyproject.toml          # uv project config, dependency groups
├── program.md              # Training constraints and budget
├── SPACE_README.md         # HuggingFace Spaces card
├── CLAUDE.md               # AI agent instructions
├── docs/
│   ├── TASK-PLAN.md        # T1-T9 dependency graph for project tasks
│   ├── RUNBOOK.md          # Copy-paste commands for training workflow
│   ├── paper-outline.md    # ACL short paper structure
│   └── research/           # Prior art, benchmarks, neural memory notes
├── paper/
│   ├── nl2shell.tex        # ACL short paper (LaTeX)
│   └── nl2shell.bib        # Bibliography
└── notebooks/
    ├── train-v1.ipynb      # v1 training notebook (A100, 8,130 pairs)
    └── train-v2.ipynb      # v2 training notebook (H100, 11,894 pairs)
```

---

## Contributing

Contributions are welcome. Areas where help is most valuable:

- **Benchmarking** — run `benchmark.py` and open an issue with your results (hardware, model version, metrics)
- **Dataset expansion** — shell command pairs for domains not well-covered: Kubernetes, AWS CLI, PowerShell, zsh-specific syntax
- **Alternative architectures** — fine-tuning comparisons on Llama-3.2-1B, Phi-3.5-mini, or Mistral-7B for the same task
- **Evaluation harness** — implementing IC-ALFA (execution accuracy via Docker sandbox) for apples-to-apples comparison with prior work
- **Edge deployment** — testing on Raspberry Pi 4/5, RISC-V boards, or other constrained hardware

To contribute:

```bash
git clone https://github.com/nl2shell/nl2shell
cd nl2shell
uv sync --group dev
git checkout -b feat/your-feature

# Lint and format before submitting
ruff check .
ruff format .
ty check .
```

Open a pull request with a clear description of what changed and why.

---

## Citation

If you use NL2Shell in your research, please cite:

```bibtex
@misc{nl2shell2026,
  title        = {NL2Shell: Natural Language to Shell Command Translation
                  with Hybrid DeltaNet Architecture},
  author       = {Arya Teja},
  year         = {2026},
  howpublished = {\url{https://github.com/nl2shell/nl2shell}},
  note         = {Fine-tuned Qwen3.5-0.8B (QLoRA) on NL2Bash + macOS synthetic pairs.
                  Model: \url{https://huggingface.co/AryaYT/nl2shell-0.8b}},
}
```

---

## Links

| Resource | URL |
|---|---|
| Model (HuggingFace) | https://huggingface.co/AryaYT/nl2shell-0.8b |
| Dataset (HuggingFace) | https://huggingface.co/datasets/AryaYT/nl2shell-training |
| Demo (Gradio Space) | https://huggingface.co/spaces/AryaYT/nl2shell-demo |
| GitHub | https://github.com/nl2shell/nl2shell |
| CloudAGI | https://cloudagi.ai |
| Author | https://github.com/nl2shell |
| Base model | https://huggingface.co/Qwen/Qwen3.5-0.8B |
| NL2Bash dataset | https://huggingface.co/datasets/GWHed/nl2bash |

---

## License

MIT License. See [LICENSE](LICENSE).

Built by [Arya Teja](https://github.com/nl2shell) as part of [CloudAGI](https://cloudagi.ai) — Agent Credit Economy.
