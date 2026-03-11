"""
NL2Shell Demo — HuggingFace Spaces Gradio App
==============================================
Converts natural language descriptions into shell commands using
the AryaYT/nl2shell-0.8b model (Qwen3.5-0.8B fine-tuned with QLoRA).

Deploy: Push this file + requirements.txt to a Gradio HF Space.
ZeroGPU: Decorate the generate() fn with @spaces.GPU if hosting
         on a ZeroGPU-enabled Space (PRO account required).
"""

import time

import gradio as gr
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MODEL_ID = "AryaYT/nl2shell-0.8b"

SYSTEM_PROMPT = (
    "You are an expert shell programmer. Given a natural language request, "
    "output ONLY the corresponding shell command. No explanations."
)

EXAMPLES = [
    "list all files in the current directory sorted by size",
    "kill the process using port 3000",
    "find all Python files modified in the last 24 hours",
    "show disk usage of the current directory",
    "count lines of code in all TypeScript files",
    "check SSL certificate expiry of example.com",
    "compress the src directory into a tar.gz",
    "show git log as one-line summaries for the last 20 commits",
    "find and delete all node_modules directories recursively",
    "show all running Docker containers",
    "list all open network connections",
    "show which process is using the most CPU",
    "generate a random 32-character password",
    "create a new git branch called feature-auth",
    "watch a directory for file changes",
]

# ---------------------------------------------------------------------------
# ZeroGPU support (no-op when not in a ZeroGPU Space)
# ---------------------------------------------------------------------------
# If you are on a ZeroGPU Space (HF PRO account), uncomment the two lines
# below and add `spaces` to requirements.txt to get free H200 access:
#
#   import spaces
#   @spaces.GPU(duration=30)
#
# The @spaces.GPU decorator is a no-op in non-ZeroGPU environments, so it's
# safe to add proactively if you have a PRO account.


# ---------------------------------------------------------------------------
# Device detection
# ---------------------------------------------------------------------------
def get_device() -> str:
    """Return the best available device string."""
    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


DEVICE = get_device()
IS_GPU = DEVICE in ("cuda", "mps")

# ---------------------------------------------------------------------------
# Model loading — happens once at startup
# ---------------------------------------------------------------------------
print(f"[NL2Shell] Loading model on {DEVICE}...")
_load_start = time.time()

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)

# On CPU (free HF Spaces tier): load in float32, no device_map needed.
# On GPU: use bfloat16 + device_map=auto for speed and memory efficiency.
if IS_GPU:
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
else:
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float32,
        trust_remote_code=True,
    )
    model = model.to(DEVICE)

model.eval()
_load_time = time.time() - _load_start
print(f"[NL2Shell] Model loaded in {_load_time:.1f}s on {DEVICE}")


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------
def build_prompt(user_request: str) -> str:
    """Build a ChatML-formatted prompt for NL2Shell."""
    return (
        f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n"
        f"<|im_start|>user\n{user_request.strip()}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )


def extract_command(full_output: str) -> str:
    """Extract the assistant's shell command from a full ChatML output string."""
    marker = "<|im_start|>assistant\n"
    if marker in full_output:
        cmd = full_output.split(marker)[-1]
        # Strip the closing im_end token if present
        cmd = cmd.split("<|im_end|>")[0]
        return cmd.strip()
    return full_output.strip()


def generate(
    user_request: str, temperature: float = 0.1, max_new_tokens: int = 128
) -> tuple[str, str]:
    """
    Run inference and return (command, metadata_markdown).

    Returns a tuple so Gradio can display command and meta info separately.
    """
    if not user_request or not user_request.strip():
        return "", "Enter a description above and click Generate."

    prompt = build_prompt(user_request)
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(DEVICE)
    input_len = input_ids.shape[1]

    t0 = time.time()
    with torch.no_grad():
        output_ids = model.generate(
            input_ids=input_ids,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=temperature > 0.0,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.convert_tokens_to_ids("<|im_end|>"),
        )
    elapsed = time.time() - t0

    full_output = tokenizer.decode(output_ids[0], skip_special_tokens=False)
    command = extract_command(full_output)

    tokens_generated = output_ids.shape[1] - input_len
    tok_per_sec = tokens_generated / elapsed if elapsed > 0 else 0

    meta = (
        f"**Device:** {DEVICE.upper()}  |  "
        f"**Tokens generated:** {tokens_generated}  |  "
        f"**Speed:** {tok_per_sec:.1f} tok/s  |  "
        f"**Time:** {elapsed:.2f}s"
    )

    return command, meta


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------
def run_example(example_text: str) -> tuple[str, str, str]:
    """Used by the Examples component — populate input and run inference."""
    cmd, meta = generate(example_text)
    return example_text, cmd, meta


# ---------------------------------------------------------------------------
# Gradio Interface
# ---------------------------------------------------------------------------
CSS = """
#header {
    text-align: center;
    margin-bottom: 8px;
}
#header h1 {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 4px;
}
#header p {
    color: #6b7280;
    font-size: 0.95rem;
}
#command-output textarea {
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 1.05rem;
    background: #0d1117;
    color: #58d68d;
    border: 1px solid #30363d;
    border-radius: 6px;
}
#meta-row {
    font-size: 0.8rem;
    color: #6b7280;
}
.gr-button-primary {
    background: #2ea44f !important;
    border: none !important;
}
"""

DESCRIPTION_MD = """\
**[AryaYT/nl2shell-0.8b](https://huggingface.co/AryaYT/nl2shell-0.8b)** \
is a 0.8B-parameter model fine-tuned from Qwen3.5-0.8B with QLoRA on the \
[NL2Bash](https://huggingface.co/datasets/jiacheng-ye/nl2bash) benchmark \
(~10,000 pairs) plus 40 hand-crafted macOS command pairs. \
It outputs **only the shell command** — no markdown, no explanation.
"""

INFO_MD = """\
| Property | Value |
|---|---|
| Base model | Qwen/Qwen3.5-0.8B |
| Fine-tuning | QLoRA (4-bit, rank 16, alpha 32) |
| Training data | NL2Bash + 40 macOS synthetic pairs |
| Format | ChatML |
| Max output | 128 tokens |
| GGUF (edge) | q4_k_m ~400 MB, q8_0 ~650 MB |
| License | MIT |

**Run locally with Ollama:**
```bash
ollama run hf.co/AryaYT/nl2shell-0.8b
```
"""

HARDWARE_NOTE = (
    "Running on **GPU** — fast inference."
    if IS_GPU
    else (
        "Running on **CPU** (free HF Spaces tier). "
        "Generation takes 5-20 seconds. "
        "For instant results, duplicate this Space and choose a GPU tier, "
        "or run the model locally via Ollama."
    )
)


def build_ui() -> gr.Blocks:
    with gr.Blocks(css=CSS, title="NL2Shell — Natural Language to Shell Commands") as demo:
        # Header
        with gr.Column(elem_id="header"):
            gr.Markdown("# NL2Shell")
            gr.Markdown(
                "Convert natural language descriptions into shell commands. "
                "No explanations — just the command."
            )

        gr.Markdown(DESCRIPTION_MD)
        gr.Markdown(f"> {HARDWARE_NOTE}")

        # Main input/output
        with gr.Row():
            with gr.Column(scale=3):
                user_input = gr.Textbox(
                    label="Describe what you want to do",
                    placeholder="e.g. find all Python files modified in the last 24 hours",
                    lines=2,
                    max_lines=4,
                )
                with gr.Row():
                    submit_btn = gr.Button("Generate Command", variant="primary")
                    clear_btn = gr.Button("Clear")

                # Advanced settings (collapsed by default)
                with gr.Accordion("Advanced settings", open=False):
                    temperature = gr.Slider(
                        minimum=0.0,
                        maximum=1.0,
                        value=0.1,
                        step=0.05,
                        label="Temperature",
                        info="Lower = more deterministic. 0.1 recommended for shell commands.",
                    )
                    max_tokens = gr.Slider(
                        minimum=16,
                        maximum=256,
                        value=128,
                        step=16,
                        label="Max new tokens",
                    )

            with gr.Column(scale=2):
                command_output = gr.Textbox(
                    label="Generated Shell Command",
                    elem_id="command-output",
                    lines=3,
                    interactive=False,
                    show_copy_button=True,
                )
                meta_output = gr.Markdown(
                    value="",
                    elem_id="meta-row",
                )

        # Examples
        gr.Markdown("### Example Prompts")
        gr.Examples(
            examples=EXAMPLES,
            inputs=user_input,
            outputs=[user_input, command_output, meta_output],
            fn=run_example,
            cache_examples=False,
            label="Click an example to run it",
        )

        # Model info
        with gr.Accordion("Model Info & Local Usage", open=False):
            gr.Markdown(INFO_MD)

        # Warning footer
        gr.Markdown(
            "> **Note:** Always review shell commands before running them, "
            "especially those involving `rm`, `kill`, `sudo`, or network operations. "
            "This model is a research demo — treat output as a starting point, not ground truth."
        )

        # Wire up events
        submit_btn.click(
            fn=generate,
            inputs=[user_input, temperature, max_tokens],
            outputs=[command_output, meta_output],
        )

        user_input.submit(
            fn=generate,
            inputs=[user_input, temperature, max_tokens],
            outputs=[command_output, meta_output],
        )

        clear_btn.click(
            fn=lambda: ("", "", ""),
            outputs=[user_input, command_output, meta_output],
        )

    return demo


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = build_ui()
    app.launch()
