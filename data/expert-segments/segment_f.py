"""
Expert-quality NL-to-shell pairs — Segment F.

Voice/Conversational Style — macOS Apple Silicon.

Categories:
  1. System Monitoring — voice-style (25 pairs)
  2. Package Management — voice-style (25 pairs)
  3. File Navigation & Management — voice-style (20 pairs)
  4. Git Daily Workflows — voice-style (20 pairs)

NL phrasing matches how a developer would speak naturally to a voice assistant.
No pair duplicates expert_pairs.py or segments A-D.
"""

PAIRS: list[tuple[str, str]] = [
    # =========================================================================
    # SYSTEM MONITORING — voice/conversational (25 pairs)
    # =========================================================================
    ("check system stats", "btop"),
    ("show CPU usage", "top -l 1 | head -5"),
    ("show memory pressure", "memory_pressure"),
    ("what processes are using the most CPU", "ps aux -r | head -10"),
    ("check battery status", "pmset -g batt"),
    ("show thermal throttling", "pmset -g therm"),
    ("check disk health", "diskutil info disk0 | grep -i 'smart\\|status'"),
    ("how hot is my Mac", "sudo powermetrics --samplers smc -i1 -n1 2>/dev/null | grep -i temp"),
    ("show network bandwidth usage", "nettop -P -L 1 -t wifi"),
    ("what's connected via USB", "system_profiler SPUSBDataType"),
    ("show all listening ports", "lsof -i -P | grep LISTEN"),
    ("how much RAM do I have free", "vm_stat | grep -E 'Pages free|Pages inactive'"),
    ("is my SSD healthy", "smartctl -a disk0 2>/dev/null || diskutil info disk0 | grep SMART"),
    ("what's eating my disk space", "du -sh ~/* 2>/dev/null | sort -rh | head -10"),
    ("show me running processes", "ps aux | head -20"),
    (
        "what's my CPU temperature right now",
        "sudo powermetrics --samplers smc -i1 -n1 2>/dev/null | grep 'CPU die'",
    ),
    ("check how long my Mac has been on", "uptime"),
    (
        "show GPU memory usage",
        "sudo powermetrics --samplers gpu_power -i1 -n1 2>/dev/null | grep -i gpu",
    ),
    ("how fast is my internet", "networkQuality"),
    ("show me disk read and write speeds", "iostat -d disk0 1 3"),
    ("what's using my network right now", "lsof -i | grep ESTABLISHED | head -20"),
    ("check available disk space", "df -h /"),
    (
        "show memory usage by app",
        "ps aux --sort=-%mem | awk 'NR<=11{print $4\"% \"$11}' | column -t",
    ),
    (
        "monitor live CPU per core",
        "sudo powermetrics --samplers cpu_power -i1000 -n3 2>/dev/null | grep -E 'CPU|%'",
    ),
    (
        "what's my Mac's model and specs",
        "system_profiler SPHardwareDataType | grep -E 'Model|Memory|Processor'",
    ),
    # =========================================================================
    # PACKAGE MANAGEMENT — voice/conversational (25 pairs)
    # =========================================================================
    ("update everything", "brew update && brew upgrade"),
    ("install ripgrep", "brew install ripgrep"),
    ("what's outdated", "brew outdated"),
    ("clean up old brew stuff", "brew cleanup --prune=7 -s"),
    ("install a cask app", "brew install --cask rectangle"),
    ("search for a package", "brew search terminal"),
    ("remove a package", "brew uninstall package-name"),
    ("show what I have installed", "brew list"),
    ("install a global npm tool", "npm install -g package-name"),
    ("check for npm vulnerabilities", "npm audit"),
    ("install with cargo", "cargo install tool-name"),
    ("update rust toolchain", "rustup update"),
    ("install a python tool globally", "pipx install tool-name"),
    ("what npm packages are outdated globally", "npm outdated -g"),
    (
        "upgrade all pip packages",
        "pip list --outdated --format=json | python3 -c \"import json,sys; [print(p['name']) for p in json.load(sys.stdin)]\" | xargs pip install -U",
    ),
    ("show me what brew services are running", "brew services list"),
    ("restart a brew service", "brew services restart postgresql@16"),
    (
        "check if a formula is installed",
        "brew list ripgrep 2>/dev/null && echo installed || echo not installed",
    ),
    ("uninstall a cask app", "brew uninstall --cask app-name"),
    ("add a new brew tap", "brew tap homebrew/cask-fonts"),
    ("show brew doctor warnings", "brew doctor"),
    ("install bun", "brew install oven-sh/bun/bun"),
    ("update bun", "bun upgrade"),
    ("list globally installed npm packages", "npm list -g --depth=0"),
    ("install all project dependencies", "bun install"),
    # =========================================================================
    # FILE NAVIGATION & MANAGEMENT — voice/conversational (20 pairs)
    # =========================================================================
    ("go to my projects folder", "cd ~/Projects"),
    ("jump to cloudagi", "z cloudagi"),
    ("show me the file tree", "eza --icons --tree --level=2"),
    ("find all typescript files", "fd -e ts"),
    ("search for TODO in the code", "rg 'TODO|FIXME' --type ts"),
    ("how big is this directory", "du -sh ."),
    ("show hidden files", "eza -la --icons"),
    ("open this in VS Code", "code ."),
    ("preview this markdown file", "glow README.md"),
    ("list only directories", "eza -D --icons"),
    ("copy a file", "cp source.txt destination.txt"),
    ("move a file to another folder", "mv file.txt ~/Documents/"),
    ("delete this file", "rm file.txt"),
    ("create a new folder", "mkdir my-new-folder"),
    ("rename a file", "mv oldname.txt newname.txt"),
    ("show the most recently changed files", "eza -la --sort=modified --icons | tail -10"),
    ("find a file by name", "fd config.json"),
    ("count how many files are in this folder", "fd -t f | wc -l"),
    ("open current folder in Finder", "open ."),
    ("show file sizes in a directory", "eza -l --sort=size --icons"),
    # =========================================================================
    # GIT DAILY WORKFLOWS — voice/conversational (20 pairs)
    # =========================================================================
    ("what did I change", "git diff"),
    ("commit everything with a message", "git add -A && git commit -m 'your message here'"),
    ("push my changes", "git push"),
    ("pull the latest", "git pull"),
    ("create a new branch", "git checkout -b feature/name"),
    ("switch to main", "git checkout main"),
    ("show recent commits", "git log --oneline -10"),
    ("stash my changes", "git stash"),
    ("undo the last commit but keep changes", "git reset --soft HEAD~1"),
    ("check the status", "git status"),
    ("show what changed in the last commit", "git show --stat HEAD"),
    (
        "pull down a remote branch",
        "git fetch origin && git checkout -b feature/name origin/feature/name",
    ),
    ("delete a local branch", "git branch -d feature/old-branch"),
    ("see who wrote this code", "git blame src/main.ts"),
    ("find when a bug was introduced", "git log --oneline --all | head -20"),
    ("sync my fork with upstream", "git fetch upstream && git rebase upstream/main"),
    ("discard my changes to a file", "git checkout -- src/file.ts"),
    ("tag the current commit", "git tag -a v1.0.0 -m 'release v1.0.0'"),
    ("push all tags", "git push --tags"),
    ("show all branches", "git branch -a"),
]
