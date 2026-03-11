"""
NL2Shell Multi-GPU Experiment Script
=====================================
Trains the same model (Qwen3.5-0.8B) on the same dataset (AryaYT/nl2shell-training)
with identical hyperparameters across different GPUs to measure quality differences.

Usage:
    python3 experiment_gpu.py              # auto-detect GPU
    python3 experiment_gpu.py --gpu a100   # override label

Results are saved to /content/experiment_results_{gpu}.json and pushed to HuggingFace.
"""

import json
import math
import os
import subprocess
import sys
import time

# ── Install dependencies ─────────────────────────────────────────────────────
print("[0/7] Installing dependencies...")
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
print("Dependencies installed.")

import torch
from datasets import load_dataset
from huggingface_hub import HfApi, create_repo, login

os.environ["WANDB_DISABLED"] = "true"

# ── Constants ────────────────────────────────────────────────────────────────
HF_TOKEN = os.environ.get("HF_TOKEN", "")
MODEL_NAME = "Qwen/Qwen3.5-0.8B"
DATASET_REPO = "AryaYT/nl2shell-training"
RESULTS_REPO = "AryaYT/nl2shell-experiments"
MAX_SEQ_LENGTH = 512

SYSTEM_PROMPT = (
    "You are an expert shell programmer. "
    "Given a natural language request, output ONLY the corresponding shell command. "
    "No explanations."
)

EVAL_PROMPTS = [
    "list all files in the current directory",
    "find all Python files larger than 1MB",
    "show the last 20 lines of a log file",
    "create a compressed backup of the home directory",
    "check which process is using port 8080",
    "show all running processes sorted by memory usage",
    "count the number of lines in all .py files recursively",
]

# ── Hyperparameters (IDENTICAL across all GPUs) ─────────────────────────────
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
NUM_EPOCHS = 4
BATCH_SIZE = 8
GRAD_ACCUM = 4
EFFECTIVE_BS = BATCH_SIZE * GRAD_ACCUM  # 32
LR = 2e-4

TARGET_MODULES = [
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj",
]


# ── GPU Detection ────────────────────────────────────────────────────────────
def detect_gpu():
    """Detect GPU type from nvidia-smi."""
    if not torch.cuda.is_available():
        return "cpu"
    name = torch.cuda.get_device_name(0).lower()
    if "h100" in name:
        return "h100"
    elif "a100" in name:
        return "a100"
    elif "l4" in name:
        return "l4"
    elif "t4" in name:
        return "t4"
    elif "v100" in name:
        return "v100"
    else:
        return name.replace(" ", "-")


# Parse CLI args
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--gpu", type=str, default=None, help="GPU label override")
args = parser.parse_args()

GPU_LABEL = args.gpu or detect_gpu()
CHECKPOINT_DIR = f"/content/nl2shell-experiment-{GPU_LABEL}"

print(f"\n{'=' * 60}")
print("  NL2Shell Multi-GPU Experiment")
print(
    f"  GPU: {GPU_LABEL} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})"
)
print(
    f"  VRAM: {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f} GB"
    if torch.cuda.is_available()
    else "  VRAM: N/A"
)
print(f"{'=' * 60}\n")

# ── Results dict — we'll accumulate metrics here ────────────────────────────
results = {
    "gpu": GPU_LABEL,
    "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
    "vram_gb": round(torch.cuda.get_device_properties(0).total_mem / 1e9, 1)
    if torch.cuda.is_available()
    else 0,
    "model": MODEL_NAME,
    "dataset": DATASET_REPO,
    "hyperparams": {
        "lora_r": LORA_R,
        "lora_alpha": LORA_ALPHA,
        "lora_dropout": LORA_DROPOUT,
        "epochs": NUM_EPOCHS,
        "batch_size": BATCH_SIZE,
        "grad_accum": GRAD_ACCUM,
        "effective_bs": EFFECTIVE_BS,
        "lr": LR,
        "scheduler": "cosine",
        "warmup": "5%",
        "max_seq_length": MAX_SEQ_LENGTH,
    },
    "training": {},
    "eval": {},
    "timestamps": {},
}

# ── HF Login ─────────────────────────────────────────────────────────────────
print("[1/7] Logging into HuggingFace...")
login(token=HF_TOKEN)

# ── Load Dataset ─────────────────────────────────────────────────────────────
print("[2/7] Loading dataset...")
raw = load_dataset(DATASET_REPO, split="train")
dataset = raw.select_columns(["text"]).shuffle(seed=42)
results["dataset_size"] = len(dataset)
print(f"  {len(dataset):,} training examples")

# ── Load Model ───────────────────────────────────────────────────────────────
print(f"[3/7] Loading {MODEL_NAME}...")
results["timestamps"]["model_load_start"] = time.time()

USE_UNSLOTH = True
try:
    from unsloth import FastLanguageModel

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=MODEL_NAME,
        max_seq_length=MAX_SEQ_LENGTH,
        dtype=None,
        load_in_4bit=True,
    )
    print("  Loaded with Unsloth FastLanguageModel (4-bit)")
except Exception as e:
    print(f"  Unsloth failed: {e}")
    USE_UNSLOTH = False
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

results["timestamps"]["model_load_end"] = time.time()
results["training"]["model_load_time_s"] = round(
    results["timestamps"]["model_load_end"] - results["timestamps"]["model_load_start"], 1
)

# ── Apply QLoRA ──────────────────────────────────────────────────────────────
print("[4/7] Applying QLoRA adapters...")
if USE_UNSLOTH:
    model = FastLanguageModel.get_peft_model(
        model,
        r=LORA_R,
        target_modules=TARGET_MODULES,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )
else:
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

    model = prepare_model_for_kbit_training(model)
    lora_config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        target_modules=TARGET_MODULES,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)

model.print_trainable_parameters()

# ── Configure Trainer ────────────────────────────────────────────────────────
from transformers import TrainingArguments
from trl import SFTTrainer

print("[5/7] Configuring trainer...")
steps_per_epoch = math.ceil(len(dataset) / EFFECTIVE_BS)
total_steps = steps_per_epoch * NUM_EPOCHS
warmup_steps = max(int(total_steps * 0.05), 20)

results["training"]["steps_per_epoch"] = steps_per_epoch
results["training"]["total_steps"] = total_steps
results["training"]["warmup_steps"] = warmup_steps

print(f"  Steps/epoch: {steps_per_epoch}, Total: {total_steps}, Warmup: {warmup_steps}")

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    dataset_num_proc=4,
    packing=True,
    args=TrainingArguments(
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM,
        warmup_steps=warmup_steps,
        num_train_epochs=NUM_EPOCHS,
        learning_rate=LR,
        fp16=False,
        bf16=True,
        logging_steps=10,
        save_steps=max(steps_per_epoch // 2, 50),
        save_total_limit=2,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="cosine",
        seed=42,
        output_dir=CHECKPOINT_DIR,
        report_to="none",
        dataloader_num_workers=4,
    ),
)

# Mask system/user tokens
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

# ── Train ────────────────────────────────────────────────────────────────────
print("[6/7] Starting training...")
results["timestamps"]["train_start"] = time.time()
trainer_stats = trainer.train()
results["timestamps"]["train_end"] = time.time()

train_time = results["timestamps"]["train_end"] - results["timestamps"]["train_start"]
results["training"]["loss"] = round(trainer_stats.training_loss, 4)
results["training"]["runtime_s"] = round(train_time, 1)
results["training"]["steps_completed"] = trainer_stats.global_step
results["training"]["steps_per_second"] = round(trainer_stats.global_step / train_time, 2)
results["training"]["samples_per_second"] = round(
    trainer_stats.metrics.get("train_samples_per_second", 0), 2
)

print("\n  Training complete!")
print(f"  Loss:        {results['training']['loss']}")
print(f"  Time:        {train_time:.0f}s ({train_time / 60:.1f} min)")
print(f"  Steps:       {trainer_stats.global_step}")
print(f"  Steps/sec:   {results['training']['steps_per_second']}")

# ── Evaluation ───────────────────────────────────────────────────────────────
print("[7/7] Running evaluation...")
if USE_UNSLOTH:
    FastLanguageModel.for_inference(model)

eval_results = []
for prompt in EVAL_PROMPTS:
    chatml_input = (
        f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n"
        f"<|im_start|>user\n{prompt}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )
    input_ids = tokenizer(chatml_input, return_tensors="pt").input_ids.to(model.device)

    t0 = time.time()
    with torch.no_grad():
        outputs = model.generate(
            input_ids=input_ids,
            max_new_tokens=128,
            temperature=0.1,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    inference_time = time.time() - t0

    full_output = tokenizer.decode(outputs[0], skip_special_tokens=False)
    if "<|im_start|>assistant\n" in full_output:
        cmd = full_output.split("<|im_start|>assistant\n")[-1]
        cmd = cmd.split("<|im_end|>")[0].strip()
    else:
        cmd = tokenizer.decode(outputs[0][input_ids.shape[1] :], skip_special_tokens=True).strip()

    tokens_generated = outputs.shape[1] - input_ids.shape[1]
    eval_results.append(
        {
            "prompt": prompt,
            "command": cmd,
            "inference_time_s": round(inference_time, 3),
            "tokens_generated": int(tokens_generated),
            "tokens_per_second": round(tokens_generated / inference_time, 1)
            if inference_time > 0
            else 0,
        }
    )
    print(f"  NL:  {prompt}")
    print(f"  CMD: {cmd}")
    print(f"  ({inference_time:.2f}s, {tokens_generated} tokens)")
    print()

results["eval"]["prompts"] = eval_results
results["eval"]["avg_inference_time_s"] = round(
    sum(r["inference_time_s"] for r in eval_results) / len(eval_results), 3
)
results["eval"]["avg_tokens_per_second"] = round(
    sum(r["tokens_per_second"] for r in eval_results) / len(eval_results), 1
)

# ── Save Results ─────────────────────────────────────────────────────────────
results_path = f"/content/experiment_results_{GPU_LABEL}.json"
with open(results_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {results_path}")

# Push results to HF
api = HfApi()
try:
    create_repo(RESULTS_REPO, private=False, exist_ok=True, repo_type="dataset")
    api.upload_file(
        path_or_fileobj=results_path,
        path_in_repo=f"results/{GPU_LABEL}.json",
        repo_id=RESULTS_REPO,
        repo_type="dataset",
    )
    print(f"  Results pushed to {RESULTS_REPO}")
except Exception as e:
    print(f"  Failed to push results: {e}")

# Print summary
print(f"\n{'=' * 60}")
print(f"  EXPERIMENT COMPLETE — {GPU_LABEL}")
print(f"  Loss: {results['training']['loss']}")
print(f"  Training time: {results['training']['runtime_s']}s")
print(f"  Steps/sec: {results['training']['steps_per_second']}")
print(f"  Avg inference: {results['eval']['avg_inference_time_s']}s")
print(f"  Avg tok/s: {results['eval']['avg_tokens_per_second']}")
print(f"{'=' * 60}")
print("EXPERIMENT_COMPLETE")
