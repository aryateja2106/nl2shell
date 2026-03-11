"""Segment H — Compact Output & Filtering Patterns (100 pairs)"""

PAIRS: list[tuple[str, str]] = [
    # =========================================================================
    # FILTERING & EXTRACTING (25 pairs)
    # =========================================================================
    # jq for JSON
    (
        "show only the name and image of each docker container",
        "docker ps --format '{{.Names}}\t{{.Image}}'",
    ),
    (
        "show only the name and status of docker containers",
        "docker ps --format '{{.Names}}\t{{.Status}}'",
    ),
    (
        "get the IP address of a docker container",
        "docker inspect mycontainer | jq -r '.[0].NetworkSettings.IPAddress'",
    ),
    (
        "get the environment variables of a docker container",
        "docker inspect mycontainer | jq -r '.[0].Config.Env[]'",
    ),
    (
        "show pod names and their status from kubectl",
        "kubectl get pods -o json | jq -r '.items[] | [.metadata.name, .status.phase] | @tsv'",
    ),
    (
        "get just the cluster server URL from kubeconfig",
        "kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}'",
    ),
    (
        "show only failed GitHub Actions runs",
        "gh run list --limit 20 --json status,name | jq -r '.[] | select(.status==\"failure\") | .name'",
    ),
    ("get the latest npm version of a package", "npm view react version"),
    (
        "pull the access_token from a curl oauth response",
        "curl -s https://api.example.com/token -d 'grant_type=client_credentials' | jq -r '.access_token'",
    ),
    ("list all keys in a JSON file", "jq 'keys' config.json"),
    ("flatten a nested JSON array to one value per line", "jq -r '.results[].name' data.json"),
    (
        "extract image names from a docker-compose config",
        "docker-compose config | yq '.services[].image' | sort -u",
    ),
    # awk/cut for columnar data
    ("show only the PID and command name from ps", "ps aux | awk '{print $2, $11}'"),
    ("show only filesystem name and percent used from df", "df -h | awk 'NR>1 {print $1, $5}'"),
    (
        "show only open files and their PIDs from lsof on port 3000",
        "lsof -i :3000 | awk 'NR>1 {print $2, $1}'",
    ),
    ("show only the second column from a CSV file", "cut -d, -f2 data.csv"),
    (
        "extract the third field from a colon-delimited file",
        "cut -d: -f3 /etc/passwd | sort -n | head -20",
    ),
    ("show unique usernames from the passwd file", "cut -d: -f1 /etc/passwd | sort"),
    # grep with context
    ("show error lines with 2 lines of context before them", "grep -B2 'ERROR' app.log | tail -30"),
    (
        "show fatal log lines with 3 lines of surrounding context",
        "grep -C3 'FATAL' /var/log/syslog | tail -40",
    ),
    ("highlight fix commits in git log", "git log --oneline | grep --color=always 'fix'"),
    ("find panic lines with 1 line of surrounding context", "rg -C1 'panic' server.log | tail -20"),
    # sed and grep for field extraction
    (
        "extract just the version number from a package.json",
        'sed -n \'s/.*"version": "\\(.*\\)".*/\\1/p\' package.json',
    ),
    ("pull out all URLs from an HTML file", "grep -oE 'https?://[^\"]+' index.html | sort -u"),
    (
        "show only non-comment non-blank lines from a config file",
        "grep -v '^[[:space:]]*#' /etc/ssh/sshd_config | grep -v '^$'",
    ),
    # =========================================================================
    # SORTING & TOP-N (20 pairs)
    # =========================================================================
    # du + sort + head
    (
        "show the 10 largest directories in the current folder",
        "du -sh */ 2>/dev/null | sort -rh | head -10",
    ),
    ("show the 5 biggest items here", "du -sh * 2>/dev/null | sort -rh | head -5"),
    (
        "show the largest files anywhere under this directory",
        "find . -type f -print0 | xargs -0 du -sh | sort -rh | head -15",
    ),
    ("find the biggest files in my home directory", "du -ah ~ 2>/dev/null | sort -rh | head -10"),
    ("show disk usage by top-level folder sorted by size", "du -sh ~/* 2>/dev/null | sort -rh"),
    # ls + head
    ("show the 10 most recently modified files", "ls -lt | head -11"),
    ("show the newest file in this directory", "ls -t | head -1"),
    ("show the 5 oldest files in this directory", "ls -ltr | head -6"),
    ("show the largest files in the current directory", "ls -lSh | head -10"),
    # ps + sort + head
    ("show the top 10 memory-hungry processes", "ps aux --sort=-%mem | head -11"),
    ("show the top 5 CPU-consuming processes", "ps aux --sort=-%cpu | head -6"),
    ("show only processes using more than 1 percent CPU", "ps aux | awk '$3 > 1.0' | sort -k3 -rn"),
    # wc + sort for line counts
    ("which Python file has the most lines", "wc -l **/*.py | sort -rn | head -5"),
    (
        "count lines in all TypeScript files and rank them",
        "find . -name '*.ts' | xargs wc -l | sort -rn | head -10",
    ),
    ("which test file is the longest", "wc -l tests/**/*.test.ts 2>/dev/null | sort -rn | head -5"),
    ("show top 5 largest log files", "ls -lSh /var/log/*.log 2>/dev/null | head -5"),
    # uniq + sort for frequency
    (
        "show the most common log levels in a log file",
        "awk '{print $3}' app.log | sort | uniq -c | sort -rn",
    ),
    (
        "find the most frequently occurring IP addresses in a log",
        "awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10",
    ),
    (
        "show which error messages appear most often",
        "grep 'ERROR' app.log | awk -F'ERROR' '{print $2}' | sort | uniq -c | sort -rn | head -10",
    ),
    (
        "show the top 10 git files touched most often",
        "git log --name-only --pretty='' | grep -v '^$' | sort | uniq -c | sort -rn | head -10",
    ),
    # =========================================================================
    # FORMATTED / COLUMNAR OUTPUT (20 pairs)
    # =========================================================================
    # column -t
    ("show environment variables in aligned columns", "env | sort | column -t -s="),
    ("display a CSV file as aligned columns in the terminal", "column -t -s, data.csv | head -20"),
    ("show /etc/passwd as a readable table", "column -t -s: /etc/passwd | head -20"),
    ("align ps output into clean columns", "ps aux | column -t | head -20"),
    # git log formatting
    (
        "show git log as one line per commit with dates",
        "git log --format='%h %ad %s' --date=short -20",
    ),
    ("show compact git log with author and relative date", "git log --format='%h %ar %an: %s' -15"),
    ("show just the commit hashes from git log", "git log --format='%H' -10"),
    ("show git log with branch graph compact", "git log --oneline --graph --decorate -20"),
    (
        "show only the files changed in the last 5 commits",
        "git log --name-only --pretty='' -5 | grep -v '^$' | sort -u",
    ),
    ("show commits grouped by author", "git shortlog -sn --no-merges | head -10"),
    # docker/kubectl formatting
    (
        "show docker images with just name and size",
        "docker images --format '{{.Repository}}:{{.Tag}}\t{{.Size}}'",
    ),
    (
        "list kubernetes pods with just name, status, and node",
        "kubectl get pods -o custom-columns='NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName'",
    ),
    # stat with format strings
    ("show file size in bytes only", "stat -f '%z' myfile.txt"),
    ("show file modification time only", "stat -f '%Sm' -t '%Y-%m-%d %H:%M' myfile.txt"),
    # printf / awk formatting
    (
        "show df output with aligned columns and human sizes",
        "df -h | awk 'NR==1 || /^\\//' | column -t",
    ),
    (
        "show network interface names and their IPs only",
        "ifconfig | awk '/^[a-z]/{iface=$1} /inet /{print iface, $2}' | column -t",
    ),
    (
        "print a summary table of file extensions and counts",
        "find . -type f | sed 's/.*\\.//' | sort | uniq -c | sort -rn | awk '{printf \"%-6s %s\\n\", $1, $2}' | head -15",
    ),
    # uptime / system info formatted
    ("show load average compact", "uptime | awk -F'load averages:' '{print \"Load:\", $2}'"),
    (
        "show memory usage as a one-liner on macOS",
        "vm_stat | awk '/free/ {free=$3} /active/ {act=$3} END {printf \"Free: %.1fGB  Active: %.1fGB\\n\", free*4096/1e9, act*4096/1e9}'",
    ),
    (
        "show running container names on one comma-separated line",
        "docker ps --format '{{.Names}}' | paste -sd, -",
    ),
    # =========================================================================
    # COUNT & SUMMARY (15 pairs)
    # =========================================================================
    # wc -l
    ("count lines in a file", "wc -l < myfile.txt"),
    ("count how many Python files are in this project", "find . -name '*.py' | wc -l"),
    ("count the number of functions in a Python file", "grep -c '^def ' module.py"),
    (
        "count total lines of TypeScript across the project",
        "find . -name '*.ts' -not -path '*/node_modules/*' | xargs wc -l | tail -1",
    ),
    # du -sh
    ("how much space does node_modules take", "du -sh node_modules"),
    ("how big is my home directory", "du -sh ~"),
    ("show disk usage summary for each top-level project folder", "du -sh ~/Projects/* | sort -rh"),
    # find + wc
    ("count how many test files exist", "find . -name '*.test.ts' | wc -l"),
    (
        "count all JSON files in the project excluding node_modules",
        "find . -name '*.json' -not -path '*/node_modules/*' | wc -l",
    ),
    # git shortlog
    ("show commit counts by author", "git shortlog -sn --no-merges"),
    (
        "show how many commits each person made this month",
        "git shortlog -sn --no-merges --since='1 month ago'",
    ),
    # uniq -c frequency counting
    (
        "show the most common HTTP status codes in an access log",
        "awk '{print $9}' access.log | sort | uniq -c | sort -rn",
    ),
    (
        "count how many times each test file was changed in git",
        "git log --name-only --pretty='' | grep '\\.test\\.' | sort | uniq -c | sort -rn | head -10",
    ),
    (
        "count open GitHub issues by label",
        "gh issue list --limit 200 --json labels | jq '[.[].labels[].name] | group_by(.) | map({label: .[0], count: length}) | sort_by(-.count)[]'",
    ),
    (
        "show how many lines each contributor added in git",
        "git log --numstat --pretty='' | awk '{add+=$1} END {print \"Lines added:\", add}'",
    ),
    # =========================================================================
    # SILENCE & SUPPRESS (10 pairs)
    # =========================================================================
    # -q / --quiet flags
    ("check if a port is open quietly", "nc -z -w2 localhost 5432 && echo open || echo closed"),
    ("run curl silently and just show the response body", "curl -s https://api.github.com/zen"),
    (
        "check if a brew package is installed without extra output",
        "brew list --formula | grep -q '^ripgrep$' && echo installed || echo missing",
    ),
    ("run make and suppress all error output", "make build 2>/dev/null"),
    # 2>/dev/null
    (
        "suppress permission errors when searching files",
        "find / -name '*.conf' 2>/dev/null | head -20",
    ),
    (
        "check if a command exists without any output",
        "command -v docker &>/dev/null && echo yes || echo no",
    ),
    ("find yaml files in /etc ignoring permission errors", "find /etc -name '*.yaml' 2>/dev/null"),
    # --no-header / tail -n +2
    ("show df output without the header line", "df -h | tail -n +2"),
    (
        "show ps output without the header sorted by memory",
        "ps aux | tail -n +2 | sort -k4 -rn | head -10",
    ),
    (
        "strip the header row from a CSV before processing",
        "tail -n +2 data.csv | cut -d, -f1,3 | sort",
    ),
    # =========================================================================
    # ONE-LINER DASHBOARDS (10 pairs)
    # =========================================================================
    (
        "quick system summary on macOS",
        "echo \"CPU: $(sysctl -n hw.ncpu) cores  RAM: $(sysctl -n hw.memsize | awk '{printf \"%.0fGB\", $1/1073741824}')  Disk: $(df -h / | awk 'NR==2{print $5}') used  Load: $(sysctl -n vm.loadavg | awk '{print $2}')\"",
    ),
    (
        "show a compact project health summary",
        "echo \"Tests: $(find . -name '*.test.ts' | wc -l | tr -d ' ')  TS files: $(find . -name '*.ts' -not -path '*/node_modules/*' | wc -l | tr -d ' ')  LOC: $(find . -name '*.ts' -not -path '*/node_modules/*' | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')\"",
    ),
    (
        "show a compact git repo status",
        "echo \"Branch: $(git branch --show-current)  Commits: $(git rev-list --count HEAD)  Dirty: $(git status --porcelain | wc -l | tr -d ' ') files\"",
    ),
    (
        "quick docker status summary",
        "echo \"Running: $(docker ps -q | wc -l | tr -d ' ')  Stopped: $(docker ps -qa --filter status=exited | wc -l | tr -d ' ')  Images: $(docker images -q | wc -l | tr -d ' ')\"",
    ),
    (
        "show my external and internal IP on one line",
        'echo "External: $(curl -s ifconfig.me)  Internal: $(ipconfig getifaddr en0)"',
    ),
    (
        "compact node project info",
        "node -e \"const p=require('./package.json'); console.log(p.name+'@'+p.version, '| node:'+process.version)\"",
    ),
    (
        "show a one-line process and memory snapshot",
        "ps aux | awk 'NR>1 {mem+=$4; cpu+=$3; count++} END {printf \"Processes: %d  Avg CPU: %.1f%%  Avg Mem: %.1f%%\\n\", count, cpu/count, mem/count}'",
    ),
    (
        "show top 3 CPU and memory consumers on one screen",
        "echo '--- CPU ---' && ps aux --sort=-%cpu | awk 'NR>1 && NR<5 {print $3\"% \"$11}' && echo '--- MEM ---' && ps aux --sort=-%mem | awk 'NR>1 && NR<5 {print $4\"% \"$11}'",
    ),
    (
        "compact kubernetes cluster summary",
        "echo \"Nodes: $(kubectl get nodes --no-headers | wc -l | tr -d ' ')  Pods: $(kubectl get pods --all-namespaces --no-headers | wc -l | tr -d ' ')  Services: $(kubectl get svc --all-namespaces --no-headers | wc -l | tr -d ' ')\"",
    ),
    (
        "show current directory summary in one line",
        "echo \"Files: $(ls | wc -l | tr -d ' ')  Dirs: $(ls -d */ 2>/dev/null | wc -l | tr -d ' ')  Size: $(du -sh . 2>/dev/null | cut -f1)  Git: $(git branch --show-current 2>/dev/null || echo none)\"",
    ),
]
