"""Segment J — Voice-Style Everyday Dev Commands (120 pairs)

The natural language side sounds like SPOKEN English — casual, no jargon.
The shell side is the EXPERT version: concise, correct redirects, modern tools.
macOS-first; cross-platform noted where natural.
Modern replacements: fd > find, rg > grep, eza > ls, bat > cat.
"""

PAIRS: list[tuple[str, str]] = [
    # -------------------------------------------------------------------------
    # Server & Process Management (20 pairs)
    # -------------------------------------------------------------------------
    ("start the server", "npm run dev"),
    ("stop the server", "kill $(lsof -ti:3000)"),
    ("restart the app", "kill $(lsof -ti:3000); npm run dev"),
    ("what's running on port 8080", "lsof -i :8080"),
    ("kill whatever's on port 3000", "lsof -ti:3000 | xargs kill"),
    ("show me all node processes", "pgrep -fl node"),
    ("how much memory is my app using", "ps aux | grep -m1 node | awk '{print $6/1024 \"MB\"}'"),
    ("is the server running", "lsof -ti:3000 >/dev/null && echo running || echo stopped"),
    ("run this in the background", "nohup ./command &>/dev/null &"),
    ("show me everything that's running", "ps aux | sort -k3 -rn | head -20"),
    ("what process is eating my CPU", "ps aux --sort=-%cpu | head -6"),
    ("kill that process", "kill -9 $(pgrep -f process_name)"),
    ("watch the logs live", "tail -f /var/log/syslog"),
    ("run these jobs in parallel", "command1 & command2 & wait"),
    ("check if the API is up", "curl -sf http://localhost:8080/health && echo up || echo down"),
    ("how many threads is my app using", "ps -M $(pgrep node) | wc -l"),
    ("limit how much CPU that process uses", "cpulimit -p $(pgrep node) -l 50"),
    ("restart nginx", "sudo nginx -s reload"),
    ("show open network connections", "lsof -i -n -P | grep LISTEN"),
    ("stop all background jobs", "kill $(jobs -p)"),
    # -------------------------------------------------------------------------
    # File Operations — Casual Phrasing (25 pairs)
    # -------------------------------------------------------------------------
    ("show me the big files", "du -sh * | sort -rh | head -10"),
    ("find that config file", "fd -t f config"),
    ("where's the package.json", "fd package.json"),
    ("what files changed today", "find . -mtime 0 -type f"),
    (
        "delete all node_modules folders",
        "find . -name node_modules -type d -prune -exec rm -rf {} +",
    ),
    ("how big is this folder", "du -sh ."),
    ("show me hidden files", "eza -la --group-directories-first"),
    ("make this file executable", "chmod +x script.sh"),
    ("what's in this file", "bat file.txt"),
    ("open this folder", "open ."),
    ("copy file contents to clipboard", "pbcopy < file.txt"),
    ("show me the last thing I downloaded", "ls -lt ~/Downloads | head -5"),
    ("find files bigger than 100MB", "fd -t f --size +100m"),
    ("empty this directory but keep the folder", "rm -rf ./dir/* ./dir/.*  2>/dev/null; true"),
    ("show me recently modified files", "fd -t f --changed-within 1d"),
    ("rename all these files at once", 'for f in *.txt; do mv "$f" "${f%.txt}.md"; done'),
    ("compare these two files", "diff <(sort file1.txt) <(sort file2.txt)"),
    (
        "find all the TODO comments in the code",
        "rg --line-number 'TODO|FIXME|HACK' --glob '*.{ts,js,py}'",
    ),
    ("remove duplicate lines from this file", "awk '!seen[$0]++' file.txt > deduped.txt"),
    ("count the lines in all these files", "wc -l **/*.ts | sort -n"),
    ("show me the folder structure", "eza --tree --level=3"),
    ("make a backup of this file", "cp file.txt file.txt.$(date +%Y%m%d)"),
    ("where is that binary installed", "which node && node --version"),
    ("watch this file for changes", "fswatch -o file.txt | xargs -n1 -I{} cat file.txt"),
    ("show me only the files git doesn't know about", "git ls-files --others --exclude-standard"),
    # -------------------------------------------------------------------------
    # Git — Conversational (20 pairs)
    # -------------------------------------------------------------------------
    ("what did I change", "git diff --stat"),
    ("save my work", "git add -A && git stash"),
    ("undo the last commit", "git reset --soft HEAD~1"),
    ("show me today's commits", "git log --oneline --since='midnight'"),
    ("who wrote this line", "git blame -L 42,42 file.py"),
    (
        "which branch has this fix",
        "git branch --contains $(git log --all --oneline | grep 'fix description' | awk '{print $1}')",
    ),
    ("go back to main", "git checkout main"),
    ("make a new branch for this feature", "git checkout -b feature/my-feature"),
    ("push my branch", "git push -u origin $(git branch --show-current)"),
    ("show me the diff for the last commit", "git show --stat HEAD"),
    (
        "clean up merged branches",
        "git branch --merged main | grep -v 'main\\|\\*' | xargs git branch -d",
    ),
    ("pull the latest changes", "git pull --rebase"),
    ("see what everyone else has been committing", "git log --oneline --all --since='1 week ago'"),
    ("squash my last three commits", "git rebase -i HEAD~3"),
    ("tag this release", "git tag -a v1.0.0 -m 'Release 1.0.0' && git push --tags"),
    (
        "find the commit that broke things",
        "git bisect start && git bisect bad HEAD && git bisect good v0.9.0",
    ),
    ("recover that file I deleted", "git checkout HEAD -- deleted-file.ts"),
    ("see what's staged", "git diff --cached --stat"),
    ("cherry-pick that fix from the other branch", "git cherry-pick <commit-hash>"),
    ("show me the full history of this file", "git log --follow --oneline -- path/to/file.ts"),
    # -------------------------------------------------------------------------
    # System Info — Quick Checks (20 pairs)
    # -------------------------------------------------------------------------
    ("how much disk space do I have", "df -h /"),
    ("what's my IP address", "curl -s ifconfig.me"),
    ("how much RAM is free", "vm_stat | awk '/free/ {print $3 * 4096 / 1048576 \" MB free\"}'"),
    ("what's my macOS version", "sw_vers"),
    ("how long has this been running", "uptime"),
    (
        "check my internet speed",
        "curl -s https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py | python3",
    ),
    ("who's logged in", "w"),
    ("what's using the most CPU", "ps aux --sort=-%cpu | head -6"),
    ("show battery percentage", "pmset -g batt | grep -o '[0-9]*%' | head -1"),
    ("is WiFi connected", "networksetup -getairportnetwork en0"),
    (
        "what hardware am I running on",
        "system_profiler SPHardwareDataType | grep -E 'Model|Chip|Memory'",
    ),
    (
        "how hot is my CPU",
        "sudo powermetrics --samplers smc -n1 2>/dev/null | grep 'CPU die temperature'",
    ),
    ("show all env variables", "env | sort"),
    ("what shell am I using", "echo $SHELL && $SHELL --version"),
    ("check if a port is open", "nc -zv host 443 2>&1"),
    ("show my DNS servers", "scutil --dns | grep nameserver | sort -u"),
    ("what's eating disk space", "du -sh /* 2>/dev/null | sort -rh | head -10"),
    ("list all installed apps", "ls /Applications | sort"),
    ("what's my hostname", "hostname"),
    ("show kernel version", "uname -r"),
    # -------------------------------------------------------------------------
    # SSH & Remote (10 pairs)
    # -------------------------------------------------------------------------
    ("connect to my server", "ssh user@host"),
    ("copy this file to the server", "scp file.txt user@host:~/"),
    ("tunnel port 3000 to remote", "ssh -L 3000:localhost:3000 user@host -N"),
    ("run a command on remote", "ssh user@host 'command && echo done'"),
    ("keep SSH alive", "ssh -o ServerAliveInterval=60 -o ServerAliveCountMax=3 user@host"),
    ("sync my local folder to the server", "rsync -avz --progress ./local/ user@host:~/remote/"),
    ("copy files from the server", "scp -r user@host:~/remote/ ./local/"),
    ("set up an SSH key", "ssh-keygen -t ed25519 -C 'me@example.com' && ssh-copy-id user@host"),
    ("check if I can reach the server", "ping -c 3 host"),
    ("jump through a bastion host", "ssh -J bastion_user@bastion_host target_user@target_host"),
    # -------------------------------------------------------------------------
    # Docker — Casual (15 pairs)
    # -------------------------------------------------------------------------
    ("start the containers", "docker compose up -d"),
    ("stop everything", "docker compose down"),
    ("show running containers", "docker ps --format 'table {{.Names}}\\t{{.Status}}\\t{{.Ports}}'"),
    ("get into the container", "docker exec -it container_name sh"),
    ("check the logs", "docker logs -f --tail 50 container_name"),
    ("clean up docker", "docker system prune -af --volumes"),
    ("rebuild the image", "docker compose build --no-cache && docker compose up -d"),
    (
        "see how big my images are",
        "docker images --format 'table {{.Repository}}\\t{{.Tag}}\\t{{.Size}}' | sort -k3 -rh",
    ),
    ("copy a file out of the container", "docker cp container_name:/path/to/file ./"),
    ("restart just one service", "docker compose restart service_name"),
    ("show container resource usage", "docker stats --no-stream"),
    ("pull the latest images", "docker compose pull"),
    ("see the container's environment", "docker exec container_name env | sort"),
    ("push my image to the registry", "docker build -t myapp:latest . && docker push myapp:latest"),
    ("run a one-off command in the container", "docker compose run --rm service_name command"),
    # -------------------------------------------------------------------------
    # Quick Utilities (10 pairs)
    # -------------------------------------------------------------------------
    ("generate a random password", "openssl rand -base64 32"),
    ("what time is it in UTC", "date -u"),
    ("convert this image to PNG", "sips -s format png image.jpg --out image.png"),
    ("compress this folder", "tar czf archive.tar.gz folder/"),
    ("calculate something quick", "python3 -c 'print(2**10)'"),
    ("open this URL", "open https://example.com"),
    ("timer for 5 minutes", "sleep 300 && say 'time is up'"),
    ("format this JSON", "pbpaste | python3 -m json.tool | pbcopy"),
    ("encode this string to base64", "echo -n 'hello' | base64"),
    ("show a calendar for this month", "cal"),
]
