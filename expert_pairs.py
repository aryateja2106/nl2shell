"""
Expert-quality natural language to shell command pairs for NL2Shell training.

Commands reflect what a senior engineer with 10+ years of experience would type —
not textbook examples. Proper quoting, error suppression, and idiomatic flag usage.
"""

EXPERT_PAIRS: list[tuple[str, str]] = [
    # =========================================================================
    # STDERR / STDOUT HANDLING (~30 pairs)
    # =========================================================================
    (
        "check if a command exists silently",
        "command -v git >/dev/null 2>&1 && echo installed || echo missing",
    ),
    ("run command and discard all output", "make build >/dev/null 2>&1"),
    ("redirect stderr to stdout and pipe", "make build 2>&1 | grep -i error"),
    ("capture stderr to a file", "./deploy.sh 2>deploy_errors.log"),
    ("capture both stdout and stderr to same file", "./script.sh >output.log 2>&1"),
    (
        "silently check if port 80 is open",
        "curl -s -o /dev/null -w '%{http_code}' http://localhost:80",
    ),
    ("suppress stderr when listing files", "ls /root 2>/dev/null"),
    ("log stdout and stderr separately", "./app.sh >stdout.log 2>stderr.log"),
    ("pipe stderr through grep while keeping stdout", "./build.sh 2>&1 1>/dev/null | grep ERROR"),
    ("run command and show only errors", "make test 2>&1 1>/dev/null"),
    ("tee stdout to file and continue piping", "build-output | tee build.log | grep -c WARN"),
    ("show only stderr output from a command", "command 2>&1 >/dev/null"),
    (
        "check if binary is in PATH",
        "command -v docker >/dev/null 2>&1 || { echo 'docker not found'; exit 1; }",
    ),
    ("suppress find permission denied errors", "find / -name '*.conf' 2>/dev/null"),
    ("pipe both stdout and stderr to less", "make 2>&1 | less"),
    ("run script and send all output to syslog", "./deploy.sh 2>&1 | logger -t deploy"),
    ("capture output of command substitution with stderr", "result=$(./check.sh 2>&1)"),
    ("discard stderr from du command", "du -sh /proc 2>/dev/null"),
    ("write stdout to file and print stderr to terminal", "./test.sh 2>&1 | tee output.txt"),
    ("check exit code after redirecting output", "ls /missing >/dev/null 2>&1; echo $?"),
    ("pipe stderr to a log file while stdout goes to terminal", "./run.sh 2>error.log"),
    ("swap stdout and stderr streams", "./script.sh 3>&1 1>&2 2>&3"),
    (
        "run command and only fail on real errors",
        "rsync -av src/ dst/ 2>&1 | grep -v 'permission denied'",
    ),
    (
        "send command output to both file and terminal",
        "curl -s https://example.com | tee response.json",
    ),
    (
        "check if curl request succeeded quietly",
        "curl -sf https://api.example.com >/dev/null && echo ok || echo fail",
    ),
    ("suppress warnings from python script", "python3 script.py 2>/dev/null"),
    ("run test suite and capture all output", "pytest 2>&1 | tee test_results.log"),
    (
        "check if process is running without output",
        "pgrep -x nginx >/dev/null 2>&1 && echo running || echo stopped",
    ),
    (
        "filter out specific error class from output",
        "ansible-playbook site.yml 2>&1 | grep -v 'WARNING'",
    ),
    (
        "stream command output to remote host",
        "tar czf - /data | ssh user@host 'cat > backup.tar.gz'",
    ),
    # =========================================================================
    # HUMAN-READABLE OUTPUT (~30 pairs)
    # =========================================================================
    (
        "show disk usage sorted by size human-readable",
        "du -sh */ 2>/dev/null | sort -rh | head -20",
    ),
    (
        "list largest files with human-readable sizes",
        "find . -type f -exec du -h {} + 2>/dev/null | sort -rh | head -20",
    ),
    ("show free memory in megabytes", "free -m"),
    ("list directory sizes sorted largest first", "du -sh ./* | sort -rh"),
    ("show total disk usage of a directory", "du -sh /var/log"),
    ("show df output in gigabytes", "df -h"),
    ("list processes sorted by memory usage", "ps aux --sort=-%mem | head -20"),
    ("display file sizes with column alignment", "ls -lh | column -t"),
    ("show network interface stats in readable form", "ifconfig | grep -E 'inet|ether|bytes'"),
    ("print number with human-readable byte suffix", "numfmt --to=iec 1073741824"),
    ("sort file sizes numerically with units", "du -h /usr/share | sort -h | tail -20"),
    ("display top processes with refresh", "top -o %CPU -n 20"),
    ("show inode usage by filesystem", "df -ih"),
    ("list files sorted by modification time", "ls -lht | head -20"),
    (
        "show per-process memory in megabytes",
        "ps -eo pid,comm,rss --sort=-rss | head -20 | awk '{printf \"%s %s %.1fM\\n\", $1, $2, $3/1024}'",
    ),
    (
        "compare two files side by side with line numbers",
        "diff --side-by-side --width=200 file1.txt file2.txt",
    ),
    ("show calendar for current month", "cal"),
    ("print file with line numbers", "cat -n file.txt"),
    ("show network connections with port names", "ss -tlnp"),
    ("show system uptime in human format", "uptime -p"),
    ("display date in ISO 8601 format", "date -u +%Y-%m-%dT%H:%M:%SZ"),
    ("show file type and encoding info", "file -i document.txt"),
    ("list block devices with sizes", "lsblk -h"),
    ("print history with timestamps", "HISTTIMEFORMAT='%F %T ' history"),
    ("show top 10 directories by size", "du -h --max-depth=1 | sort -rh | head -10"),
    ("display bandwidth usage per interface", "nload -u M eth0"),
    ("show routing table in readable format", "netstat -rn"),
    ("print environment variables sorted", "env | sort"),
    ("display mounted filesystems in columns", "mount | column -t"),
    ("check current timezone and time offset", "date +%Z%z"),
    # =========================================================================
    # PIPE MASTERY (~40 pairs)
    # =========================================================================
    (
        "extract unique IP addresses from nginx access log",
        "awk '{print $1}' /var/log/nginx/access.log | sort -u",
    ),
    (
        "show top 10 most frequent HTTP status codes",
        "awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -10",
    ),
    (
        "count lines of code per file type in a project",
        "find . -type f | sed 's/.*\\.//' | sort | uniq -c | sort -rn",
    ),
    (
        "find duplicate files by checksum",
        "find . -type f -exec md5sum {} + | sort | awk 'NR>1 && prev==$1{print $2} {prev=$1; file=$2}'",
    ),
    (
        "show most common words in a file",
        "tr -s ' ' '\\n' < README.md | tr '[:upper:]' '[:lower:]' | sort | uniq -c | sort -rn | head -20",
    ),
    ("extract all URLs from an HTML file", "grep -oP 'https?://[^\"\\s]+' index.html | sort -u"),
    (
        "show failed SSH login attempts by IP",
        "grep 'Failed password' /var/log/auth.log | awk '{print $11}' | sort | uniq -c | sort -rn | head -10",
    ),
    (
        "find all TODO comments in a project",
        "grep -rn 'TODO\\|FIXME\\|HACK' --include='*.py' . | grep -v '.pyc'",
    ),
    ("count git commits by author", "git log --format='%aN' | sort | uniq -c | sort -rn"),
    (
        "monitor real-time error rate in log",
        "tail -f /var/log/app.log | grep --line-buffered ERROR | pv -l -i 5 >/dev/null",
    ),
    (
        "extract JSON values from log lines",
        "grep 'response' app.log | awk -F'\"duration\":' '{print $2}' | cut -d',' -f1 | sort -n",
    ),
    (
        "show all open file handles for a process",
        "lsof -p $(pgrep nginx) | awk '{print $NF}' | sort | uniq -c | sort -rn",
    ),
    (
        "find and count all unique user agents",
        "awk -F'\"' '{print $6}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -20",
    ),
    (
        "extract all email addresses from files",
        "grep -roP '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}' . | grep -oP '[^ ]+@[^ ]+' | sort -u",
    ),
    (
        "watch log for new errors and beep",
        'tail -f app.log | grep --line-buffered -i error | while read line; do echo "$line"; tput bel; done',
    ),
    (
        "top 5 slowest endpoints in access log",
        "awk '{print $NF, $7}' /var/log/nginx/access.log | sort -rn | head -5",
    ),
    (
        "show bandwidth per process",
        "nethogs -t 2>/dev/null | awk 'NR>3 {print $1, $2}' | sort -k2 -rn | head -10",
    ),
    (
        "find all large files and sort by size",
        "find . -type f -size +10M -exec du -sh {} + | sort -rh | head -20",
    ),
    (
        "count http requests per minute from log",
        "awk '{print $4}' /var/log/nginx/access.log | cut -d: -f1-3 | uniq -c",
    ),
    (
        "show cpu usage per core",
        'mpstat -P ALL 1 1 | awk \'/^[0-9]/ && $2!="all" {print "CPU"$2": "$12"%"}\'',
    ),
    (
        "find files modified in the last hour",
        "find . -type f -newer <(date -d '1 hour ago' +'%Y%m%d%H%M') 2>/dev/null",
    ),
    (
        "show disk io by process",
        "iotop -b -n 2 | awk 'NR>3 {print $1, $4, $6, $12}' | sort -k2 -rn | head -10",
    ),
    ("extract all function names from python file", "grep -oP '^def \\K[a-zA-Z_]+' module.py"),
    ("show unique packages installed", "dpkg -l | awk '/^ii/ {print $2}' | cut -d: -f1 | sort"),
    (
        "find most recently changed config files",
        "find /etc -name '*.conf' -type f -printf '%T@ %p\\n' 2>/dev/null | sort -rn | head -10 | awk '{print $2}'",
    ),
    (
        "count lines in all python files",
        "find . -name '*.py' -type f | xargs wc -l 2>/dev/null | sort -rn | tail -1",
    ),
    (
        "list all docker image sizes sorted",
        "docker images --format '{{.Size}}\\t{{.Repository}}:{{.Tag}}' | sort -rh",
    ),
    (
        "show 5 minute load average continuously",
        "while true; do uptime | awk '{print $(NF-2)}' | tr -d ','; sleep 5; done",
    ),
    (
        "extract all cron jobs for all users",
        "for user in $(cut -d: -f1 /etc/passwd); do crontab -u $user -l 2>/dev/null | grep -v '^#' | awk -v u=$user '{print u\": \"$0}'; done",
    ),
    (
        "show memory usage trend every 2 seconds",
        'while true; do free -m | awk \'NR==2 {print strftime("%H:%M:%S"), $3"MB used"}\'; sleep 2; done',
    ),
    (
        "find files with world-write permission",
        "find / -type f -perm -o+w 2>/dev/null | grep -v '/proc\\|/sys'",
    ),
    (
        "show unique source IPs hitting 404s",
        "awk '$9==404 {print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -20",
    ),
    (
        "extract slow queries from mysql log",
        "awk '/^# Query_time:/ {print $3}' /var/log/mysql/slow.log | sort -rn | head -10",
    ),
    (
        "list all npm scripts in package json",
        "jq -r '.scripts | to_entries[] | .key + \": \" + .value' package.json",
    ),
    ("compare sorted outputs of two files", "comm -3 <(sort file1.txt) <(sort file2.txt)"),
    (
        "show which services are consuming most memory",
        "systemctl list-units --type=service --state=running | grep -oP '[^ ]+\\.service' | xargs -I{} sh -c 'echo -n \"{}: \"; systemctl show {} -p MemoryCurrent 2>/dev/null'",
    ),
    ("extract just filenames from full paths", "find . -name '*.js' | xargs -I{} basename {}"),
    ("count words per line in a file", 'awk \'{print NR": "NF" words: "$0}\' file.txt | head -20'),
    ("show all sockets with their programs", "ss -tlnup 2>/dev/null | column -t"),
    (
        "monitor file descriptor count for pid",
        "while true; do ls /proc/$(pgrep node)/fd 2>/dev/null | wc -l; sleep 1; done",
    ),
    # =========================================================================
    # PROCESS SUBSTITUTION AND SUBSHELLS (~20 pairs)
    # =========================================================================
    ("compare output of two commands side by side", "diff <(ls dir1) <(ls dir2)"),
    ("watch a log file and highlight errors", "tail -f file.log | grep --line-buffered 'ERROR'"),
    ("diff current branch against main", "diff <(git show main:src/app.py) src/app.py"),
    ("join two sorted file lists", "comm -12 <(sort files1.txt) <(sort files2.txt)"),
    (
        "run command in subshell to avoid affecting current shell",
        "(cd /tmp && tar xzf archive.tar.gz)",
    ),
    ("capture command output into variable cleanly", "count=$(wc -l < data.csv)"),
    (
        "use process substitution to avoid temp files",
        "paste <(cut -d, -f1 a.csv) <(cut -d, -f2 b.csv)",
    ),
    (
        "find files not in a reference list",
        "comm -23 <(find . -name '*.py' | sort) <(sort known_files.txt)",
    ),
    (
        "execute commands in subshell and export result",
        "export VERSION=$(git describe --tags --abbrev=0)",
    ),
    ("run parallel jobs and collect results", "paste <(cmd1) <(cmd2) <(cmd3)"),
    (
        "diff two remote files without downloading",
        "diff <(ssh host1 cat /etc/hosts) <(ssh host2 cat /etc/hosts)",
    ),
    ("tee output to command and file simultaneously", "ls | tee >(wc -l) | head -5"),
    ("run multiple commands and compare", "diff <(echo 'expected') <(./run_test.sh)"),
    ("load file content into variable stripping newlines", "content=$(tr -d '\\n' < config.json)"),
    ("use process substitution with sort unique", "sort -u <(cat list1.txt) <(cat list2.txt)"),
    ("run command with modified PATH in subshell", "(PATH=/usr/local/bin:$PATH command)"),
    ("measure time of subshell block", "time (sleep 1 && echo done)"),
    ("execute block in background subshell", "(./long_job.sh && notify-send 'done') &"),
    (
        "sum numbers across multiple files",
        "cat <(cut -d' ' -f2 a.txt) <(cut -d' ' -f2 b.txt) | awk '{s+=$1}END{print s}'",
    ),
    (
        "run conditional block in subshell without cd pollution",
        "(cd /repo && git pull && make build) && echo 'build ok'",
    ),
    # =========================================================================
    # XARGS AND FIND PATTERNS (~25 pairs)
    # =========================================================================
    ("delete all .pyc files safely", "find . -name '*.pyc' -type f -print0 | xargs -0 rm -f"),
    (
        "compress all log files older than 7 days",
        "find /var/log -name '*.log' -mtime +7 -exec gzip {} +",
    ),
    (
        "run command on each found file in parallel",
        "find . -name '*.py' -print0 | xargs -0 -P4 pylint",
    ),
    (
        "convert all png to jpg in directory",
        "find . -name '*.png' -print0 | xargs -0 -I{} convert {} {}.jpg",
    ),
    ("find empty directories and remove them", "find . -type d -empty -print0 | xargs -0 rmdir"),
    (
        "grep recursively with null delimiters for safety",
        "find . -name '*.go' -print0 | xargs -0 grep -l 'TODO'",
    ),
    (
        "chmod all scripts in a directory",
        "find ./scripts -name '*.sh' -type f -print0 | xargs -0 chmod +x",
    ),
    (
        "copy files found by pattern to directory",
        "find . -name '*.conf' -print0 | xargs -0 -I{} cp {} /backup/",
    ),
    (
        "run tests on all changed files",
        "git diff --name-only HEAD | grep '\\.test\\.ts$' | xargs -I{} bun test {}",
    ),
    (
        "find files larger than 100MB and list them",
        "find / -type f -size +100M -print0 2>/dev/null | xargs -0 du -sh | sort -rh",
    ),
    (
        "delete files older than 30 days in tmp",
        "find /tmp -type f -mtime +30 -print0 | xargs -0 rm -f",
    ),
    (
        "rename all files to lowercase",
        'find . -type f -name \'*[A-Z]*\' -print0 | xargs -0 -I{} sh -c \'mv "$1" "$(echo "$1" | tr A-Z a-z)"\' _ {}',
    ),
    (
        "grep pattern across all yaml files",
        "find . -name '*.yaml' -o -name '*.yml' | xargs grep -l 'replicas'",
    ),
    (
        "run formatter on all modified files",
        "git status --short | awk '{print $2}' | grep '\\.go$' | xargs gofmt -w",
    ),
    (
        "batch resize images in subdirectories",
        "find . -name '*.jpg' -print0 | xargs -0 -P8 -I{} convert {} -resize '1920x1080>' {}",
    ),
    (
        "find files not modified in 90 days",
        "find . -type f -not -newer <(date -d '90 days ago' +'%Y%m%d') 2>/dev/null | head -20",
    ),
    (
        "search for pattern in compressed logs",
        "find /var/log -name '*.gz' | xargs zgrep -l 'ERROR'",
    ),
    (
        "calculate total size of found files",
        "find . -name '*.log' -print0 | xargs -0 du -sc | tail -1",
    ),
    (
        "remove node_modules from all subdirectories",
        "find . -name 'node_modules' -type d -prune -print0 | xargs -0 rm -rf",
    ),
    (
        "count total lines across all source files",
        "find . -name '*.ts' -not -path '*/node_modules/*' -print0 | xargs -0 wc -l | tail -1",
    ),
    (
        "find world-readable private keys",
        "find ~ -name '*.pem' -o -name 'id_rsa' 2>/dev/null | xargs -I{} ls -la {}",
    ),
    (
        "strip whitespace from filenames",
        "find . -name '* *' -print0 | xargs -0 -I{} bash -c 'mv \"$1\" \"${1// /_}\"' _ {}",
    ),
    (
        "find recently modified config files",
        "find /etc -name '*.conf' -newer /etc/os-release -print0 2>/dev/null | xargs -0 ls -la",
    ),
    (
        "replace string in all matching files",
        "find . -name '*.html' -print0 | xargs -0 sed -i '' 's/old_domain/new_domain/g'",
    ),
    (
        "archive found files preserving paths",
        "find ./src -name '*.ts' -print0 | xargs -0 tar czf source.tar.gz",
    ),
    # =========================================================================
    # macOS-SPECIFIC IDIOMS (~30 pairs)
    # =========================================================================
    ("copy current directory path to clipboard", "pwd | pbcopy"),
    ("search for files by content on macOS", "mdfind 'kMDItemTextContent == \"search term\"'"),
    ("prevent Mac from sleeping while running a command", "caffeinate -i ./long_build.sh"),
    ("open current directory in Finder", "open ."),
    ("copy file contents to clipboard", "pbcopy < ~/.ssh/id_rsa.pub"),
    ("paste clipboard contents into file", "pbpaste > output.txt"),
    ("spotlight search for file by name", "mdfind -name 'config.json'"),
    ("speak text aloud from command line", "say 'Build complete'"),
    ("open URL in default browser", "open https://docs.example.com"),
    ("flush macOS DNS cache", "sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder"),
    ("show macOS software update list", "softwareupdate -l"),
    (
        "change default screenshot location",
        "defaults write com.apple.screencapture location ~/Desktop/Screenshots",
    ),
    ("show all running apps via launchctl", "launchctl list | grep -v '^-'"),
    ("open file with specific application", "open -a 'Visual Studio Code' ."),
    ("show macOS hardware info", "system_profiler SPHardwareDataType"),
    ("convert file encoding on macOS", "iconv -f utf-16 -t utf-8 input.txt > output.txt"),
    ("get UUID of a mac volume", "diskutil info / | awk '/Volume UUID/ {print $3}'"),
    (
        "show wifi network password for saved network",
        "security find-generic-password -wa 'NetworkName'",
    ),
    ("list all Homebrew installed packages", "brew list --formula"),
    ("check which app is listening on port", "lsof -nP -iTCP -sTCP:LISTEN | grep ':8080'"),
    ("disable Gatekeeper temporarily", "sudo spctl --master-disable"),
    ("show macOS version and build", "sw_vers"),
    ("hide a file on macOS", "chflags hidden ~/Documents/hidden_folder"),
    ("reveal a hidden file on macOS", "chflags nohidden ~/Documents/hidden_folder"),
    (
        "lock screen from command line",
        "/System/Library/CoreServices/Menu\\ Extras/User.menu/Contents/Resources/CGSession -suspend",
    ),
    ("show disk usage for Time Machine backups", "du -sh /Volumes/*/Backups.backupdb 2>/dev/null"),
    ("list installed Homebrew casks", "brew list --cask"),
    (
        "set desktop wallpaper via command line",
        'osascript -e \'tell app "Finder" to set desktop picture to POSIX file "/path/to/image.jpg"\'',
    ),
    ("show all environment variables set in launchd", "launchctl environ"),
    ("eject a disk from command line", "diskutil eject /Volumes/ExternalDrive"),
    # =========================================================================
    # ONE-LINER PATTERNS (~25 pairs)
    # =========================================================================
    ("create directory and cd into it", "mkdir -p newdir && cd newdir"),
    ("retry a command up to 3 times", "for i in 1 2 3; do command && break || sleep 1; done"),
    ("run command only if previous succeeded", "make build && make test && make deploy"),
    (
        "run fallback command if first fails",
        "pg_dump mydb > backup.sql || echo 'backup failed' | mail -s 'alert' admin@example.com",
    ),
    ("start a quick python http server", "python3 -m http.server 8080"),
    (
        "create and activate a virtual environment",
        "python3 -m venv .venv && source .venv/bin/activate",
    ),
    ("kill process on a specific port", "lsof -ti:3000 | xargs kill -9"),
    ("time a command and show result", "time ./benchmark.sh"),
    ("reload shell config without restart", "source ~/.zshrc"),
    ("backup a file before editing", "cp config.yml{,.bak}"),
    ("quickly generate a random password", "openssl rand -base64 32"),
    ("create a timestamped backup", "cp important.txt important.txt.$(date +%Y%m%d%H%M%S)"),
    ("run command every 2 seconds and clear screen", "watch -n2 'kubectl get pods'"),
    (
        "quickly check if remote host is up",
        "ping -c1 -W1 192.168.1.1 >/dev/null 2>&1 && echo up || echo down",
    ),
    ("generate a uuid", "uuidgen | tr '[:upper:]' '[:lower:]'"),
    ("get the last field from each line", "awk '{print $NF}' file.txt"),
    ("print the nth line of a file", "awk 'NR==42' file.txt"),
    ("delete blank lines from file", "sed -i '' '/^[[:space:]]*$/d' file.txt"),
    ("run multiple commands in parallel and wait", "cmd1 & cmd2 & cmd3 & wait"),
    ("create a sparse file of specific size", "truncate -s 1G bigfile.img"),
    ("quickly diff two command outputs", "diff <(sort a.txt) <(sort b.txt)"),
    (
        "append timestamp to each log line",
        'tail -f app.log | while IFS= read -r line; do echo "$(date +%T) $line"; done',
    ),
    (
        "convert unix timestamp to human date",
        "date -d @1700000000 2>/dev/null || date -r 1700000000",
    ),
    ("find and kill zombie processes", "ps aux | awk '$8==\"Z\" {print $2}' | xargs -r kill -9"),
    ("reload nginx without downtime", "nginx -t && nginx -s reload"),
    # =========================================================================
    # JSON / API HANDLING (~25 pairs)
    # =========================================================================
    (
        "fetch JSON API and extract a field",
        "curl -sf https://api.example.com/data | jq '.results[].name'",
    ),
    (
        "POST JSON data to an API",
        "curl -sf -X POST -H 'Content-Type: application/json' -d '{\"key\":\"value\"}' https://api.example.com",
    ),
    ("get HTTP response code of a URL", "curl -so /dev/null -w '%{http_code}' https://example.com"),
    ("pretty print a json file", "jq . data.json"),
    ("filter JSON array by field value", "jq '[.[] | select(.status == \"active\")]' users.json"),
    ("extract nested JSON field", "curl -sf https://api.example.com | jq -r '.data.user.email'"),
    ("count items in JSON array", "jq '.results | length' response.json"),
    ("transform JSON array to CSV", "jq -r '.[] | [.id, .name, .email] | @csv' users.json"),
    (
        "add auth header to curl request",
        'curl -sf -H "Authorization: Bearer $TOKEN" https://api.example.com/me',
    ),
    (
        "follow redirects and show final URL",
        "curl -sI -L https://short.url | grep -i location | tail -1",
    ),
    (
        "download file and show progress",
        "curl -L --progress-bar -o output.zip https://example.com/archive.zip",
    ),
    (
        "send multipart form data",
        "curl -sf -F 'file=@photo.jpg' -F 'name=test' https://upload.example.com",
    ),
    (
        "paginate through API and collect all results",
        "for page in $(seq 1 10); do curl -sf \"https://api.example.com/items?page=$page\"; done | jq -s 'add'",
    ),
    ("check API health endpoint", "curl -sf https://api.example.com/health | jq -r '.status'"),
    ("update a JSON field in a file", "jq '.version = \"2.0\"' package.json | sponge package.json"),
    ("merge two JSON objects", "jq -s '.[0] * .[1]' base.json override.json"),
    ("extract all keys from JSON object", "jq 'keys[]' config.json"),
    (
        "convert JSON to environment variables",
        "jq -r 'to_entries[] | \"export \\(.key)=\\(.value)\"' config.json",
    ),
    (
        "fetch URL with timeout and retry",
        "curl -sf --retry 3 --retry-delay 2 --max-time 10 https://api.example.com",
    ),
    (
        "query JSON with multiple conditions",
        "jq '.[] | select(.age > 18 and .active == true) | .name' users.json",
    ),
    (
        "post raw json from file",
        "curl -sf -X POST -H 'Content-Type: application/json' -d @payload.json https://api.example.com",
    ),
    ("get response headers only", "curl -sI https://example.com"),
    (
        "send DELETE request to API",
        'curl -sf -X DELETE -H "Authorization: Bearer $TOKEN" https://api.example.com/resource/123',
    ),
    ("validate json file syntax", "jq empty data.json && echo valid || echo invalid"),
    ("sort json array by field", "jq 'sort_by(.created_at) | reverse' events.json"),
    # =========================================================================
    # GIT EXPERT PATTERNS (~25 pairs)
    # =========================================================================
    ("show files changed in the last commit", "git diff --name-only HEAD~1"),
    (
        "find which commit introduced a bug",
        "git bisect start && git bisect bad HEAD && git bisect good v1.0",
    ),
    ("show commits by author this week", "git log --author='name' --since='1 week ago' --oneline"),
    ("amend last commit without changing message", "git commit --amend --no-edit"),
    ("show what branch a commit is on", "git branch -a --contains abc1234"),
    ("undo last commit but keep changes staged", "git reset --soft HEAD~1"),
    ("stash only unstaged changes", "git stash -u -k"),
    ("cherry pick a range of commits", "git cherry-pick abc123..def456"),
    ("show all tags sorted by date", "git tag --sort=-creatordate | head -10"),
    ("clean untracked files and directories", "git clean -fd"),
    ("show file history with diffs", "git log -p --follow -- src/auth.ts"),
    ("find who changed a specific line", "git log -S 'suspicious_function' --oneline"),
    ("create a branch from a specific commit", "git checkout -b hotfix/issue-123 abc1234"),
    ("show diff for staged changes", "git diff --cached"),
    ("rebase interactively last 5 commits", "git rebase -i HEAD~5"),
    ("show all aliases configured", "git config --list | grep alias"),
    (
        "count commits per day this month",
        "git log --since='1 month ago' --format='%ad' --date=short | sort | uniq -c",
    ),
    ("push new branch and set upstream", "git push -u origin $(git branch --show-current)"),
    ("show branches merged into main", "git branch --merged main | grep -v main"),
    (
        "delete all merged local branches",
        "git branch --merged | grep -v '\\*\\|main\\|master\\|dev' | xargs git branch -d",
    ),
    (
        "show largest files in git history",
        "git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | awk '/^blob/{print $3, $4}' | sort -rn | head -10",
    ),
    ("squash all commits on feature branch", "git rebase -i $(git merge-base HEAD main)"),
    ("show changed files between two branches", "git diff --name-only main..feature/branch"),
    ("pull and rebase instead of merge", "git pull --rebase origin main"),
    ("show git log as a graph", "git log --oneline --graph --all --decorate | head -30"),
    # =========================================================================
    # DOCKER / CONTAINER PATTERNS (~20 pairs)
    # =========================================================================
    ("remove all stopped containers and dangling images", "docker system prune -f"),
    ("follow logs of a running container", "docker logs -f --tail 100 container_name"),
    ("run interactive shell in running container", "docker exec -it container_name bash"),
    (
        "list all containers with resource usage",
        "docker stats --no-stream --format 'table {{.Name}}\\t{{.CPUPerc}}\\t{{.MemUsage}}'",
    ),
    ("build image and tag it", "docker build -t myapp:$(git rev-parse --short HEAD) ."),
    ("pull latest and restart container", "docker pull myimage:latest && docker-compose up -d"),
    ("copy file from container to host", "docker cp container_name:/app/config.json ./config.json"),
    (
        "inspect container environment variables",
        "docker inspect container_name | jq '.[0].Config.Env[]'",
    ),
    ("remove all images matching a pattern", "docker images 'myapp*' -q | xargs docker rmi"),
    ("run container and remove when done", "docker run --rm -it ubuntu:22.04 bash"),
    (
        "show container IP address",
        "docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' container_name",
    ),
    ("list all docker volumes", "docker volume ls --format 'table {{.Name}}\\t{{.Driver}}'"),
    (
        "run command in new container with volume mount",
        "docker run --rm -v $(pwd):/work -w /work node:20 npm install",
    ),
    ("save image to tar archive", "docker save myapp:latest | gzip > myapp.tar.gz"),
    ("load image from archive", "docker load < myapp.tar.gz"),
    ("force recreate all containers in compose", "docker-compose up -d --force-recreate"),
    (
        "check container health status",
        "docker inspect --format='{{.State.Health.Status}}' container_name",
    ),
    ("limit container memory and cpu", "docker run -m 512m --cpus=1.5 myapp"),
    (
        "push image to registry",
        "docker tag myapp:latest registry.example.com/myapp:latest && docker push registry.example.com/myapp:latest",
    ),
    ("get container start time", "docker inspect -f '{{.State.StartedAt}}' container_name"),
    # =========================================================================
    # NETWORK / SECURITY (~20 pairs)
    # =========================================================================
    ("check all listening ports with process names", "ss -tlnp"),
    ("create SSH tunnel for local development", "ssh -NL 5432:localhost:5432 user@remote"),
    ("scan for open ports on a host", "nmap -T4 -F 192.168.1.1"),
    (
        "check SSL certificate expiry",
        "echo | openssl s_client -connect example.com:443 2>/dev/null | openssl x509 -noout -dates",
    ),
    ("test if a TCP port is open", "nc -zv -w3 192.168.1.10 5432 2>&1"),
    (
        "capture HTTP traffic on an interface",
        "tcpdump -i eth0 -n 'tcp port 80' -A 2>/dev/null | head -100",
    ),
    ("block an IP with iptables", "iptables -A INPUT -s 192.168.1.100 -j DROP"),
    ("check who is connected to this host", "ss -tnp | grep ESTABLISHED"),
    ("trace the route to a host", "traceroute -n google.com"),
    ("show all active network connections", "ss -tunap"),
    ("check DNS resolution for a domain", "dig +short example.com"),
    ("test SMTP server connectivity", "nc -zv mail.example.com 587 2>&1"),
    ("show iptables rules with line numbers", "iptables -L -n -v --line-numbers"),
    ("query a specific DNS server", "dig @8.8.8.8 example.com"),
    ("run port scan against subnet", "nmap -sn 192.168.1.0/24"),
    ("check certificate chain", "openssl s_client -connect example.com:443 -showcerts 2>/dev/null"),
    ("monitor network traffic in real time", "iftop -n -P -i eth0"),
    ("reverse DNS lookup for IP", "dig -x 8.8.8.8 +short"),
    ("test UDP port is reachable", "nc -zuv 192.168.1.10 514 2>&1"),
    ("show all network interfaces and IPs", "ip -brief addr show"),
    # =========================================================================
    # TEXT PROCESSING POWER (~25 pairs)
    # =========================================================================
    ("extract the 3rd column from a CSV", "cut -d',' -f3 data.csv"),
    ("replace all tabs with 4 spaces in a file", "sed -i '' 's/\t/    /g' file.txt"),
    (
        "print lines matching a pattern with context",
        "grep -C3 'NullPointerException' app.log | head -30",
    ),
    ("remove duplicate lines preserving order", "awk '!seen[$0]++' file.txt"),
    ("reverse the order of lines in a file", "tail -r file.txt"),
    ("sum a column of numbers in a file", "awk '{sum+=$1}END{print sum}' numbers.txt"),
    ("print lines between two patterns", "awk '/START/,/END/' logfile.txt"),
    ("convert CSV to TSV", "sed 's/,/\t/g' data.csv > data.tsv"),
    ("print unique lines from two files", "sort file1.txt file2.txt | uniq -u"),
    ("extract IP addresses from file", "grep -oE '([0-9]{1,3}\\.){3}[0-9]{1,3}' file.txt"),
    ("join two files on first column", "join <(sort -k1 file1.txt) <(sort -k1 file2.txt)"),
    ("convert lowercase to uppercase", "tr '[:lower:]' '[:upper:]' < input.txt"),
    ("count occurrences of pattern per file", "grep -c 'ERROR' *.log | sort -t: -k2 -rn"),
    ("delete first n lines of file", "sed -i '' '1,5d' file.txt"),
    ("add line numbers to output", "cat -n file.txt"),
    ("extract everything between brackets", "grep -oP '\\[\\K[^\\]]+' file.txt"),
    ("replace text only on lines matching pattern", "sed '/include/s/foo/bar/g' file.txt"),
    ("show only non-empty lines", "grep -v '^[[:space:]]*$' file.txt"),
    (
        "transpose a CSV file",
        "awk -F, '{for(i=1;i<=NF;i++) a[i]=a[i]?a[i]\",\"$i:$i} END{for(i=1;i<=length(a);i++) print a[i]}' data.csv",
    ),
    ("find lines longer than 100 characters", "awk 'length>100' file.txt"),
    ("split file at blank lines into chunks", "csplit file.txt '/^$/' {*}"),
    ("print every nth line", "awk 'NR%5==0' file.txt"),
    ("count character frequency in file", "fold -w1 file.txt | sort | uniq -c | sort -rn"),
    ("strip ANSI color codes from file", "sed 's/\\x1B\\[[0-9;]*[mGKHF]//g' colored.txt"),
    ("extract version number from string", "echo 'v2.13.4' | grep -oP '[0-9]+\\.[0-9]+\\.[0-9]+'"),
    # =========================================================================
    # MODERN CLI TOOLS (~15 pairs)
    # =========================================================================
    ("find Python files ignoring node_modules", "fd -e py --exclude node_modules"),
    ("search for TODO comments in source code", "rg 'TODO|FIXME|HACK' --type py"),
    ("view file with syntax highlighting", "bat --style=full src/app.ts"),
    ("list files in tree format with icons", "eza --tree --icons --level=3 src/"),
    ("search for pattern across git history", "rg 'password' --hidden -g '!.git'"),
    ("check disk usage with visual bars", "dust -r /var/log"),
    ("show process tree with resource usage", "procs --tree"),
    ("find files by name fast", "fd config --type f"),
    ("grep with context and color", "rg 'import' --type ts -C2 src/"),
    ("interactive fuzzy file finder", "fzf --preview 'bat --color=always {}'"),
    (
        "list recent git commits with pretty format",
        "git log --oneline | fzf --preview 'git show {1}'",
    ),
    ("watch directory for changes", "fd . src/ | entr -r ./run.sh"),
    ("show http response with colors", "http GET https://api.example.com/users"),
    ("interactive process manager", "procs --sortd cpu"),
    (
        "list directory as tree excluding git dirs",
        "eza --tree --ignore-glob='.git|node_modules' --level=4",
    ),
    # =========================================================================
    # SYSTEM ADMINISTRATION (~20 pairs)
    # =========================================================================
    ("check system logs for last boot", "journalctl -b -1 --no-pager | tail -50"),
    (
        "reload systemd and restart a service",
        "systemctl daemon-reload && systemctl restart app.service",
    ),
    ("show service status and last log lines", "systemctl status nginx -n 20"),
    ("add user to a group", "usermod -aG docker $USER"),
    ("schedule a command with at", "echo './cleanup.sh' | at 3am"),
    ("check failed systemd units", "systemctl --failed"),
    ("show all cron jobs for current user", "crontab -l"),
    (
        "add a cron job without overwriting existing",
        "(crontab -l 2>/dev/null; echo '0 2 * * * /opt/backup.sh') | crontab -",
    ),
    ("show kernel messages since boot", "dmesg --human --since '1 hour ago'"),
    ("send test email from command line", "echo 'test' | mail -s 'test subject' admin@example.com"),
    (
        "check if a systemd service is running",
        "systemctl is-active --quiet nginx && echo running || echo stopped",
    ),
    ("follow system journal in real time", "journalctl -f -u app.service"),
    ("rotate logs manually", "logrotate -f /etc/logrotate.conf"),
    ("show open file handles count system-wide", "cat /proc/sys/fs/file-nr"),
    ("check memory pressure", "vmstat -s | head -10"),
    ("show cpu info", "lscpu | grep -E 'Model|CPU\\(s\\)|Thread|Core'"),
    (
        "monitor system calls of a process",
        "strace -p $(pgrep app) -e trace=network 2>&1 | head -50",
    ),
    ("check current ulimits", "ulimit -a"),
    ("set max open files for session", "ulimit -n 65536"),
    ("show all mounted filesystems with options", "findmnt --output TARGET,SOURCE,FSTYPE,OPTIONS"),
    # =========================================================================
    # DEVELOPMENT WORKFLOW (~20 pairs)
    # =========================================================================
    (
        "start development server and open browser",
        "npm run dev & sleep 2 && open http://localhost:3000",
    ),
    ("run tests and watch for changes", "bun test --watch"),
    ("check for security vulnerabilities in dependencies", "npm audit --production"),
    ("update all outdated npm packages", "npx npm-check-updates -u && npm install"),
    (
        "generate a self-signed certificate",
        "openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.pem -out cert.pem -subj '/CN=localhost'",
    ),
    ("run linter and fix auto-fixable issues", "eslint --fix src/**/*.ts"),
    ("check typescript errors without emitting", "tsc --noEmit"),
    ("install exact version of package", "npm install --save-exact lodash@4.17.21"),
    (
        "profile node application cpu usage",
        "node --prof app.js && node --prof-process isolate-*.log | head -30",
    ),
    (
        "search across project excluding generated dirs",
        "rg 'SearchTerm' --glob '!{node_modules,.git,dist,build}'",
    ),
    ("watch and rebuild on change", "nodemon --watch src --ext ts --exec 'ts-node src/index.ts'"),
    ("run a one-off database migration", "DATABASE_URL=$DB_URL prisma migrate deploy"),
    ("format all source files in place", "prettier --write 'src/**/*.{ts,tsx,js}'"),
    (
        "check what changed since last tag",
        "git diff $(git describe --tags --abbrev=0)..HEAD --stat",
    ),
    ("measure build time precisely", "time make clean && time make build"),
    ("install pre-commit hooks", "pre-commit install"),
    (
        "run database in docker for local dev",
        "docker run -d --name localdb -e POSTGRES_PASSWORD=dev -p 5432:5432 postgres:15",
    ),
    ("list all available npm scripts", "npm run 2>&1 | grep -A1 'available via'"),
    (
        "check if a port is already in use before starting",
        "lsof -i:8080 >/dev/null 2>&1 && echo 'port in use' || npm start",
    ),
    ("benchmark a command with multiple runs", "hyperfine --warmup 3 './my_command arg'"),
]

# Sanity check at import time
assert len(EXPERT_PAIRS) >= 300, f"Expected >= 300 pairs, got {len(EXPERT_PAIRS)}"
