"""
NL2Shell — Dataset & Evaluation Utilities (IMMUTABLE)
=====================================================
Provides dataset loading, formatting, and evaluation for NL2Shell training.
Do NOT modify this file during training — edit train.py instead.
"""

import os

from datasets import Dataset, load_dataset

# ── Constants ──────────────────────────────────────────────────────────────────
MODEL_NAME = "Qwen/Qwen3.5-0.8B"
OUTPUT_REPO = "AryaYT/nl2shell-0.8b"
MAX_SEQ_LENGTH = 512
HF_TOKEN = os.environ.get("HF_TOKEN", "")

SYSTEM_PROMPT = "You are an expert shell programmer. Given a natural language request, output ONLY the corresponding shell command. No explanations."

# ── macOS Synthetic Pairs ──────────────────────────────────────────────────────
MACOS_PAIRS = [
    ("list all installed homebrew packages", "brew list"),
    ("update homebrew and upgrade all packages", "brew update && brew upgrade"),
    ("show disk usage of current directory", "du -sh ."),
    ("find all Python files modified in the last 24 hours", "find . -name '*.py' -mtime -1"),
    ("show all running Docker containers", "docker ps"),
    ("kill the process using port 3000", "lsof -ti:3000 | xargs kill -9"),
    ("create a new git branch called feature-auth", "git checkout -b feature-auth"),
    ("show git log as one-line summaries", "git log --oneline -20"),
    ("compress the src directory into a tar.gz", "tar -czf src.tar.gz src/"),
    ("show system memory usage", "vm_stat | head -10"),
    ("list all open network connections", "lsof -i -P -n | head -20"),
    ("recursively find files larger than 100MB", "find / -size +100M -type f 2>/dev/null"),
    ("show the last 50 lines of the system log", "tail -50 /var/log/system.log"),
    (
        "restart the DNS cache on macOS",
        "sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder",
    ),
    ("show all environment variables containing PATH", "env | grep PATH"),
    ("count lines of code in all TypeScript files", "find . -name '*.ts' | xargs wc -l"),
    ("check if port 8080 is in use", "lsof -i :8080"),
    ("show the top 10 largest files in current directory", "ls -lhS | head -10"),
    ("create an SSH tunnel from local 8080 to remote 80", "ssh -L 8080:localhost:80 user@host"),
    ("watch a directory for file changes", "fswatch -r . | head -20"),
    ("install a package globally with npm", "npm install -g package-name"),
    ("run a Python HTTP server on port 8000", "python3 -m http.server 8000"),
    ("show all cron jobs for current user", "crontab -l"),
    (
        "check SSL certificate expiry of a domain",
        "echo | openssl s_client -connect example.com:443 2>/dev/null | openssl x509 -noout -dates",
    ),
    ("search for a string recursively in all files", "grep -r 'search_string' ."),
    ("show CPU and memory usage of all processes", "top -l 1 | head -20"),
    ("generate a random 32-character password", "openssl rand -base64 32"),
    ("download a file with curl and save it", "curl -LO https://example.com/file.tar.gz"),
    ("show the size of each subdirectory", "du -sh */ | sort -rh"),
    ("list all git branches sorted by last commit date", "git branch --sort=-committerdate"),
    ("set a file as executable", "chmod +x script.sh"),
    ("show the difference between two files", "diff file1.txt file2.txt"),
    (
        "find and delete all node_modules directories",
        "find . -name 'node_modules' -type d -prune -exec rm -rf {} +",
    ),
    ("show which process is using the most CPU", "ps aux --sort=-%cpu | head -5"),
    ("create a symbolic link", "ln -s /path/to/original /path/to/link"),
    ("watch the output of a command every 2 seconds", "watch -n 2 'command'"),
    ("show all listening TCP ports", "netstat -tlnp 2>/dev/null || ss -tlnp"),
    ("convert a video to mp4 using ffmpeg", "ffmpeg -i input.mov -c:v libx264 -c:a aac output.mp4"),
    ("show git stash list", "git stash list"),
    ("run a command in the background and disown it", "nohup command &>/dev/null & disown"),
]

# ── Eval Test Prompts ──────────────────────────────────────────────────────────
EVAL_PROMPTS = [
    "list all files in the current directory",
    "find all Python files larger than 1MB",
    "show the last 20 lines of a log file",
    "create a compressed backup of the home directory",
    "check which process is using port 8080",
    "show all running processes sorted by memory usage",
    "count the number of lines in all .py files recursively",
]


def format_chatml(nl: str, cmd: str) -> str:
    """Format a single NL/CMD pair as ChatML."""
    return (
        f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n"
        f"<|im_start|>user\n{nl}<|im_end|>\n"
        f"<|im_start|>assistant\n{cmd}<|im_end|>"
    )


def get_dataset() -> Dataset:
    """Load NL2Bash + macOS synthetic pairs, formatted as ChatML text."""
    # Load NL2Bash
    print("Loading NL2Bash dataset...")
    try:
        nl2bash = load_dataset("GWHed/nl2bash", split="train")
        nl_col, cmd_col = "nl", "bash"
        print(f"  GWHed/nl2bash: {len(nl2bash)} examples")
    except Exception as e:
        print(f"  GWHed/nl2bash failed: {e}, trying fallback...")
        nl2bash = load_dataset("AnishJoshi/nl2bash-custom", split="train")
        nl_col, cmd_col = "nl_command", "bash_code"
        print(f"  AnishJoshi/nl2bash-custom: {len(nl2bash)} examples")

    # Format NL2Bash as ChatML
    nl2bash_texts = []
    for row in nl2bash:
        nl = row[nl_col].strip()
        cmd = row[cmd_col].strip()
        if nl and cmd:
            nl2bash_texts.append(format_chatml(nl, cmd))

    # Format macOS pairs as ChatML
    macos_texts = [format_chatml(nl, cmd) for nl, cmd in MACOS_PAIRS]

    # Combine
    all_texts = nl2bash_texts + macos_texts
    dataset = Dataset.from_dict({"text": all_texts})
    dataset = dataset.shuffle(seed=42)
    print(f"Total training examples: {len(dataset)}")
    return dataset


def run_eval(model, tokenizer) -> None:
    """Run 7 test prompts through the model and print NL -> CMD."""
    print("\n" + "=" * 60)
    print("EVALUATION")
    print("=" * 60)

    for prompt in EVAL_PROMPTS:
        chatml_input = (
            f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n"
            f"<|im_start|>user\n{prompt}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )
        inputs = tokenizer(chatml_input, return_tensors="pt").to(model.device)

        outputs = model.generate(
            **inputs,
            max_new_tokens=128,
            temperature=0.1,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )

        full_output = tokenizer.decode(outputs[0], skip_special_tokens=False)
        # Extract assistant response
        if "<|im_start|>assistant\n" in full_output:
            cmd = full_output.split("<|im_start|>assistant\n")[-1]
            cmd = cmd.split("<|im_end|>")[0].strip()
        else:
            cmd = tokenizer.decode(
                outputs[0][inputs["input_ids"].shape[1] :],
                skip_special_tokens=True,
            ).strip()

        print(f"  NL:  {prompt}")
        print(f"  CMD: {cmd}")
        print()
