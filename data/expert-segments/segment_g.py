"""
Expert-quality NL-to-shell pairs - Segment G.

Categories:
  1. AI Agent Invocation (28 pairs) -- claude, amp, codex, gemini, cursor agent,
     cline, opencode, kiro, jules, auggie; voice-style NL, real CLI flags
  2. Cloud & Deployment (22 pairs) -- gcloud, supabase, netlify, tailscale,
     cloudflared; project-specific patterns
  3. SSH & Remote Workflows (20 pairs) -- ground-control.online, tmux sessions,
     rsync, scp, remote one-liners
  4. Ollama & Local AI (15 pairs) -- model management, serve, run, nl2shell model

No overlap with expert_pairs.py or segments A-D.
All commands are real, single-line, conversational-NL quality.
"""

PAIRS: list[tuple[str, str]] = [
    # =========================================================================
    # AI AGENT INVOCATION (28 pairs)
    # =========================================================================
    # claude
    ("ask claude to review this code", "claude 'review this code for bugs'"),
    ("start claude in plan mode", "claude --plan"),
    ("start claude without permission prompts", "claude --dangerously-skip-permissions"),
    ("open a fresh claude session with no context", "claude --no-auto-approve"),
    ("ask claude to explain the current directory", "claude 'explain what this project does'"),
    ("have claude write tests for this file", "claude 'write unit tests for src/auth.ts'"),
    ("ask claude to fix the failing test", "claude 'fix the failing test in tests/api.test.ts'"),
    ("ask claude to summarize the last commit", "claude 'summarize the changes in HEAD'"),
    ("continue the last claude conversation", "claude --continue"),
    ("run claude in verbose mode", "claude --verbose"),
    # amp
    ("ask amp to fix this bug", "amp 'fix the failing test'"),
    ("check amp credits remaining", "amp usage"),
    ("start amp with a specific task", "amp 'implement pagination for the users endpoint'"),
    (
        "ask amp to review the pull request",
        "amp 'review the open pull request for security issues'",
    ),
    ("run amp and open a new chat", "amp"),
    # codex
    ("run codex in safe mode", "codex --sandbox read-only 'explain this function'"),
    ("run codex review on the last commit", "codex review HEAD~1..HEAD"),
    (
        "ask codex to refactor this module",
        "codex 'refactor src/database.ts to use connection pooling'",
    ),
    (
        "start codex with full auto approval",
        "codex --approval-mode full-auto 'add error handling to all API routes'",
    ),
    (
        "ask codex to explain this codebase",
        "codex 'give me an overview of the project architecture'",
    ),
    # gemini
    ("ask gemini about the architecture", "gemini 'what is the architecture of this project'"),
    ("run gemini with a prompt file", "gemini -p prompt.txt"),
    ("ask gemini to compare two approaches", "gemini 'compare REST vs GraphQL for this API'"),
    # cursor agent / other agents
    ("start cursor agent", "agent"),
    ("ask opencode to implement a feature", "opencode 'add dark mode toggle to the dashboard'"),
    ("run kiro on this project", "kiro"),
    ("ask all agents for opinions", "council 'best approach for caching this dataset'"),
    (
        "get a council decision on the architecture",
        "council 'should we use Redis or an in-memory cache here'",
    ),
    # =========================================================================
    # CLOUD & DEPLOYMENT (22 pairs)
    # =========================================================================
    # gcloud Cloud Run
    (
        "deploy to Cloud Run from source",
        "gcloud run deploy cloudagi --source . --region us-central1 --allow-unauthenticated",
    ),
    (
        "check Cloud Run logs for my service",
        "gcloud run services logs read cloudagi --region us-central1 --limit 50",
    ),
    ("list my gcloud projects", "gcloud projects list"),
    ("switch gcloud project", "gcloud config set project my-project-id"),
    ("show the active gcloud configuration", "gcloud config list"),
    (
        "authenticate gcloud with application default credentials",
        "gcloud auth application-default login",
    ),
    ("describe a Cloud Run service", "gcloud run services describe cloudagi --region us-central1"),
    (
        "update Cloud Run traffic to the latest revision",
        "gcloud run services update-traffic cloudagi --to-latest --region us-central1",
    ),
    (
        "list Cloud Run revisions",
        "gcloud run revisions list --service cloudagi --region us-central1",
    ),
    (
        "build and push a container image to Artifact Registry",
        "gcloud builds submit --tag gcr.io/my-project/myapp:latest .",
    ),
    # supabase
    ("start supabase locally", "supabase start"),
    ("check supabase status", "supabase status"),
    ("stop supabase local instance", "supabase stop"),
    ("run supabase migrations", "supabase db push"),
    ("open supabase studio in the browser", "supabase studio"),
    (
        "generate supabase typescript types",
        "supabase gen types typescript --local > src/types/supabase.ts",
    ),
    # netlify
    ("push to netlify production", "netlify deploy --prod"),
    ("preview a netlify deployment", "netlify deploy"),
    ("check netlify deploy status", "netlify status"),
    ("open the netlify admin dashboard", "netlify open"),
    # tailscale
    ("connect to my tailnet", "tailscale up"),
    ("check tailscale status", "tailscale status"),
    # =========================================================================
    # SSH & REMOTE WORKFLOWS (20 pairs)
    # =========================================================================
    # ground-control.online patterns
    ("connect to ground control", "ssh -t ground-control.online"),
    (
        "start a tmux session on the remote server",
        "ssh -t ground-control.online 'tmux attach -t main 2>/dev/null || tmux new -s main'",
    ),
    (
        "open a remote shell in my main tmux session",
        "ssh -t ground-control.online 'tmux new-window'",
    ),
    (
        "run a command on the remote server without staying connected",
        "ssh ground-control.online 'df -h && free -m'",
    ),
    ("check what is running on the server", "ssh ground-control.online 'ps aux | head -20'"),
    (
        "tail the app logs on the remote server",
        "ssh ground-control.online 'tail -f /var/log/app/app.log'",
    ),
    # scp / rsync file transfer
    ("copy a file to the remote server", "scp file.txt arya@ground-control.online:~/"),
    ("copy a file from the server to local", "scp arya@ground-control.online:~/output.csv ./"),
    (
        "sync my project to the server excluding node_modules",
        "rsync -avz --exclude node_modules --exclude .git ./ arya@ground-control.online:~/project/",
    ),
    (
        "sync server logs to local for analysis",
        "rsync -avz arya@ground-control.online:/var/log/app/ ./logs/",
    ),
    (
        "dry run rsync to preview what would be transferred",
        "rsync -avzn --exclude node_modules ./ arya@ground-control.online:~/project/",
    ),
    # cloudflared
    (
        "expose local port to internet with cloudflared",
        "cloudflared tunnel --url http://localhost:3000",
    ),
    (
        "expose local development server on port 8080",
        "cloudflared tunnel --url http://localhost:8080",
    ),
    # tmux local session management
    ("list all tmux sessions", "tmux ls"),
    ("start a new named tmux session", "tmux new -s work"),
    ("attach to the main tmux session", "tmux attach -t main"),
    ("detach from tmux", "tmux detach"),
    ("split the current tmux pane vertically", "tmux split-window -h"),
    ("split the current tmux pane horizontally", "tmux split-window -v"),
    ("kill a tmux session by name", "tmux kill-session -t old-session"),
    # =========================================================================
    # OLLAMA & LOCAL AI (15 pairs)
    # =========================================================================
    ("start ollama server", "ollama serve"),
    ("run a local llama model", "ollama run llama3.2"),
    ("run the nl2shell model locally", "ollama run hf.co/AryaYT/nl2shell-0.8b"),
    ("run qwen locally for coding tasks", "ollama run qwen2.5-coder:7b"),
    (
        "run a model and pass a prompt directly",
        "ollama run llama3.2 'explain what this error means'",
    ),
    ("list all installed ollama models", "ollama list"),
    ("pull a new model to ollama", "ollama pull qwen2.5:7b"),
    ("pull the latest mistral model", "ollama pull mistral"),
    ("show which ollama models are currently loaded in memory", "ollama ps"),
    ("remove an ollama model to free disk space", "ollama rm llama3.1"),
    ("check ollama version", "ollama version"),
    ("stop the ollama server process", "pkill ollama"),
    ("copy a model to a new name in ollama", "ollama cp llama3.2 my-custom-llama"),
    ("push a local ollama model to a registry", "ollama push my-org/my-model"),
    ("show details about an installed model", "ollama show llama3.2"),
]

assert len(PAIRS) >= 80, f"Expected >= 80 pairs, got {len(PAIRS)}"
