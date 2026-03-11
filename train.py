"""
NL2Shell — Training Script (AGENT-EDITABLE)
============================================
Fine-tunes Qwen3.5-0.8B on NL2Bash + macOS synthetic pairs using QLoRA.
Designed to run on Google Colab A100 via lecoder-cgpu.

Usage:
  python3 train.py
"""

import os
import subprocess
import sys

# ── Install Dependencies ───────────────────────────────────────────────────────
print("[0/6] Installing dependencies...")
subprocess.check_call(
    [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-q",
        "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git",
    ]
)
subprocess.check_call(
    [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-q",
        "--no-deps",
        "trl",
        "peft",
        "accelerate",
        "bitsandbytes",
    ]
)
subprocess.check_call(
    [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-q",
        "datasets",
        "huggingface_hub",
    ]
)

os.environ["WANDB_DISABLED"] = "true"

# ── Imports ────────────────────────────────────────────────────────────────────
import torch
from huggingface_hub import HfApi, create_repo, login

from prepare import (
    HF_TOKEN,
    MAX_SEQ_LENGTH,
    MODEL_NAME,
    OUTPUT_REPO,
    get_dataset,
    run_eval,
)

# ── HuggingFace Login ─────────────────────────────────────────────────────────
print("[1/6] Logging into HuggingFace...")
login(token=HF_TOKEN)

# ── Load Model ─────────────────────────────────────────────────────────────────
print(f"[2/6] Loading {MODEL_NAME}...")

USE_UNSLOTH = True
try:
    from unsloth import FastLanguageModel

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=MODEL_NAME,
        max_seq_length=MAX_SEQ_LENGTH,
        dtype=None,
        load_in_4bit=True,
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )
    print("  Loaded with Unsloth FastLanguageModel (4-bit QLoRA)")

except Exception as e:
    print(f"  Unsloth failed: {e}")
    print("  Falling back to standard transformers + PEFT...")
    USE_UNSLOTH = False

    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    print("  Loaded with transformers + PEFT (4-bit QLoRA)")

model.print_trainable_parameters()

# ── Load Dataset ───────────────────────────────────────────────────────────────
print("[3/6] Preparing dataset...")
dataset = get_dataset()

# ── Training ───────────────────────────────────────────────────────────────────
print("[4/6] Training...")

import math

from transformers import TrainingArguments
from trl import SFTTrainer

num_epochs = 3
batch_size = 8
grad_accum = 4
effective_batch = batch_size * grad_accum
steps_per_epoch = math.ceil(len(dataset) / effective_batch)
total_steps = steps_per_epoch * num_epochs
save_steps = max(steps_per_epoch // 2, 50)

print(f"  Examples:     {len(dataset)}")
print(f"  Epochs:       {num_epochs}")
print(f"  Batch:        {batch_size} x {grad_accum} = {effective_batch} effective")
print(f"  Steps/epoch:  {steps_per_epoch}")
print(f"  Total steps:  {total_steps}")
print(f"  Save every:   {save_steps} steps")

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    dataset_num_proc=2,
    packing=True,
    args=TrainingArguments(
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=grad_accum,
        warmup_steps=20,
        num_train_epochs=num_epochs,
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=10,
        save_steps=save_steps,
        save_total_limit=2,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="cosine",
        seed=42,
        output_dir="/content/nl2shell-checkpoints",
        report_to="none",
    ),
)

# Mask user/system tokens — only train on assistant responses
try:
    from unsloth.chat_templates import train_on_responses_only

    trainer = train_on_responses_only(
        trainer,
        instruction_part="<|im_start|>user\n",
        response_part="<|im_start|>assistant\n",
    )
    print("  train_on_responses_only applied")
except Exception as e:
    print(f"  train_on_responses_only skipped: {e}")

trainer_stats = trainer.train()
print("\nTraining complete!")
print(f"  Loss: {trainer_stats.training_loss:.4f}")
print(f"  Time: {trainer_stats.metrics['train_runtime']:.0f}s")

# ── Evaluation ─────────────────────────────────────────────────────────────────
print("[5/6] Running evaluation...")
if USE_UNSLOTH:
    FastLanguageModel.for_inference(model)
run_eval(model, tokenizer)

# ── Export & Push ──────────────────────────────────────────────────────────────
print("[6/6] Exporting and pushing to HuggingFace...")

api = HfApi()
create_repo(OUTPUT_REPO, private=False, exist_ok=True)

# Save merged 16-bit model
if USE_UNSLOTH:
    model.save_pretrained_merged("/content/nl2shell-merged", tokenizer, save_method="merged_16bit")

    # Export GGUF
    print("  Exporting GGUF q4_k_m...")
    try:
        model.save_pretrained_gguf(
            "/content/nl2shell-gguf-q4", tokenizer, quantization_method="q4_k_m"
        )
        print("    q4_k_m done")
    except Exception as e:
        print(f"    q4_k_m failed: {e}")

    print("  Exporting GGUF q8_0...")
    try:
        model.save_pretrained_gguf(
            "/content/nl2shell-gguf-q8", tokenizer, quantization_method="q8_0"
        )
        print("    q8_0 done")
    except Exception as e:
        print(f"    q8_0 failed: {e}")

    # Push merged model
    model.push_to_hub(OUTPUT_REPO, tokenizer=tokenizer)
    print("  Merged model pushed")

    # Push GGUF files
    for gguf_dir in ["/content/nl2shell-gguf-q4", "/content/nl2shell-gguf-q8"]:
        if os.path.exists(gguf_dir):
            for f in os.listdir(gguf_dir):
                if f.endswith(".gguf"):
                    api.upload_file(
                        path_or_fileobj=os.path.join(gguf_dir, f),
                        path_in_repo=f"gguf/{f}",
                        repo_id=OUTPUT_REPO,
                    )
                    print(f"    Uploaded {f}")
else:
    # Standard PEFT: push adapter, user merges later
    model.push_to_hub(OUTPUT_REPO)
    tokenizer.push_to_hub(OUTPUT_REPO)
    print("  LoRA adapter pushed (merge manually for GGUF)")

# Upload model card
MODEL_CARD = """---
license: mit
base_model: Qwen/Qwen3.5-0.8B
tags:
  - nl2bash
  - shell
  - terminal
  - command-line
  - qwen3.5
  - qlora
  - lecoder
  - cloudagi
datasets:
  - jiacheng-ye/nl2bash
language:
  - en
pipeline_tag: text-generation
---

# NL2Shell 0.8B — Natural Language to Shell Commands

Ultra-lightweight model for converting natural language to Unix/macOS shell commands.
Fine-tuned from Qwen3.5-0.8B using QLoRA on NL2Bash + 40 custom macOS command pairs.

## Usage

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("AryaYT/nl2shell-0.8b")
tokenizer = AutoTokenizer.from_pretrained("AryaYT/nl2shell-0.8b")

prompt = "<|im_start|>system\\nYou are an expert shell programmer. Given a natural language request, output ONLY the corresponding shell command. No explanations.<|im_end|>\\n<|im_start|>user\\nlist all files in the current directory<|im_end|>\\n<|im_start|>assistant\\n"
inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=64)
print(tokenizer.decode(outputs[0], skip_special_tokens=False))
```

### With Ollama (GGUF)
```bash
# Q4_K_M (~400MB) for Raspberry Pi / edge
# Q8_0 (~650MB) for Mac / desktop
ollama run hf.co/AryaYT/nl2shell-0.8b
```

## Training Details
- **Base:** Qwen/Qwen3.5-0.8B
- **Method:** QLoRA (rank 16, alpha 32, all linear layers)
- **Data:** NL2Bash + 40 macOS synthetic pairs
- **Epochs:** 3
- **Hardware:** Google Colab A100
- **Built by:** [Arya Teja](https://aryateja.com) | [CloudAGI](https://cloudagi.ai)
"""

api.upload_file(
    path_or_fileobj=MODEL_CARD.encode(),
    path_in_repo="README.md",
    repo_id=OUTPUT_REPO,
)
print("  Model card uploaded")

print(f"\nModel live at: https://huggingface.co/{OUTPUT_REPO}")
print("TRAINING_COMPLETE")
