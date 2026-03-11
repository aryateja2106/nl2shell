"""
Expert-quality NL-to-shell pairs — Segment E.

Focus: VOICE/CONVERSATIONAL natural language — how developers SPEAK to a terminal
assistant, not how they type. NL side uses contractions, questions, casual phrasing.

Categories:
  1. Project Development Workflows (30 pairs)
     — bun, cargo, npm, pnpm dev patterns; spoken dev commands
  2. Natural Conversational Commands (28 pairs)
     — casual spoken queries: "what's on port 3000", "show me what's eating memory"
  3. Container & Service Management — Voice Style (15 pairs)
     — Docker/OrbStack spoken commands
  4. Task Runner / Justfile Patterns (12 pairs)
     — just, make, voice-style task invocations

No overlap with expert_pairs.py or segments A-D.
"""

PAIRS: list[tuple[str, str]] = [
    # =========================================================================
    # 1. PROJECT DEVELOPMENT WORKFLOWS (30 pairs)
    # =========================================================================
    # Bun
    ("start the dev server with bun", "bun run dev"),
    ("run the tests with bun", "bun test"),
    ("run bun tests and rerun on file change", "bun test --watch --bail"),
    ("build the project with bun", "bun run build"),
    ("install all the dependencies with bun", "bun install"),
    ("add a package with bun", "bun add zod"),
    ("remove a package with bun", "bun remove lodash"),
    ("add a dev dependency with bun", "bun add -d @types/node"),
    ("run a script from package json with bun", "bun run lint"),
    ("upgrade all bun dependencies", "bun update"),
    ("check what bun version I have", "bun --version"),
    ("run a single test file with bun", "bun test src/auth.test.ts"),
    # npm / pnpm
    ("start the dev server", "npm run dev"),
    ("run the tests", "npm test"),
    ("build the project", "npm run build"),
    ("check for type errors", "npx tsc --noEmit"),
    ("install the dependencies", "npm install"),
    ("what scripts are available", "npm run"),
    ("lint and fix the code", "npm run lint -- --fix"),
    ("update all dependencies", "npm update"),
    ("add typescript as a dev dependency", "npm install -D typescript"),
    ("run just the failing tests", "npm test -- --bail"),
    ("check for security vulnerabilities", "npm audit"),
    ("install packages with pnpm", "pnpm install"),
    ("add a package with pnpm", "pnpm add express"),
    ("run dev with pnpm", "pnpm dev"),
    # Cargo / Rust
    ("run cargo tests", "cargo test"),
    ("check for Rust warnings", "cargo clippy --all-targets"),
    ("build the Rust project", "cargo build"),
    ("build Rust in release mode", "cargo build --release"),
    ("run the Rust project", "cargo run"),
    # =========================================================================
    # 2. NATURAL CONVERSATIONAL COMMANDS (28 pairs)
    # =========================================================================
    # Port and process queries
    ("what's running on port 3000", "lsof -ti:3000"),
    ("what's using port 8080", "lsof -nP -iTCP:8080 -sTCP:LISTEN"),
    ("kill whatever is on port 3000", "fuser -k 3000/tcp"),
    ("show me what's eating memory", "ps aux --sort=-%mem | head -10"),
    ("show me what's using the most CPU", "ps aux --sort=-%cpu | head -10"),
    # Disk and system
    ("how much disk space do I have left", "df -h /"),
    ("how long has the system been running", "uptime"),
    ("what's my IP address", "curl -s ifconfig.me"),
    ("am I connected to the internet", "ping -c1 8.8.8.8 >/dev/null 2>&1 && echo yes || echo no"),
    ("show me the wifi network I'm on", "networksetup -getairportnetwork en0"),
    # Git conversational
    ("what branch am I on", "git branch --show-current"),
    ("what changed since yesterday", "git log --since='yesterday' --oneline"),
    ("who last touched this file", "git log -1 --format='%an %ar' -- README.md"),
    ("show me what I've changed", "git diff"),
    ("show me what's staged", "git diff --name-only --cached"),
    ("what files did I change", "git status --short"),
    ("undo my last commit but keep the changes", "git reset --soft HEAD~1 --quiet"),
    ("push my current branch up", "git push --set-upstream origin HEAD"),
    ("sync my branch with the latest from main", "git fetch origin && git rebase origin/main"),
    ("stash what I'm working on", "git stash push -m 'wip'"),
    ("pop my stash back", "git stash pop"),
    # macOS / system info
    ("pop this folder open in Finder", "open -a Finder ."),
    ("copy that to my clipboard", "pbcopy"),
    ("what version of node am I using", "node --version"),
    ("what version of Python is installed", "python3 --version"),
    ("show me the last few commands I ran", "history | tail -20"),
    ("reload my shell config", "exec zsh"),
    ("open the current directory in VS Code", "code ."),
    # =========================================================================
    # 3. CONTAINER & SERVICE MANAGEMENT — VOICE STYLE (15 pairs)
    # =========================================================================
    ("show me what containers are running", "docker ps"),
    ("start up the docker compose stack", "docker compose up -d"),
    ("bring down the docker compose stack", "docker compose down"),
    ("check the logs for the web container", "docker compose logs -f --tail 50 web"),
    ("check the logs for the database container", "docker logs -f --tail 50 postgres"),
    ("restart the web container", "docker compose restart web"),
    ("get a shell inside the container", "docker exec -it web /bin/sh"),
    ("rebuild and restart the containers", "docker compose up -d --build"),
    ("how much space are my docker images taking up", "docker system df"),
    ("clean up all the docker stuff I don't need", "docker system prune -af --volumes"),
    ("pull the latest images", "docker compose pull"),
    ("stop all the running containers", "docker compose stop"),
    (
        "show me which containers crashed recently",
        "docker ps -a --filter 'status=exited' --format 'table {{.Names}}\\t{{.Status}}'",
    ),
    ("show me the environment variables in the container", "docker exec web env | sort"),
    ("force recreate all the containers", "docker compose up -d --force-recreate"),
    # =========================================================================
    # 4. TASK RUNNER / JUSTFILE PATTERNS (12 pairs)
    # =========================================================================
    ("what tasks are available", "just --list"),
    ("run the deploy task", "just deploy"),
    ("run tests in watch mode", "just test-watch"),
    ("format all the code", "just fmt"),
    ("run the build task", "just build"),
    ("run the lint task", "just lint"),
    ("run the setup task", "just setup"),
    ("run the dev task", "just dev"),
    ("run the clean task", "just clean"),
    ("run the release task", "just release"),
    ("preview what a recipe does without running it", "just --dry-run build"),
    ("show me the source of a just recipe", "just --show dev"),
]
