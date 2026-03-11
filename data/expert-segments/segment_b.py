"""
Expert-quality NL-to-shell pairs — Segment B.

Covers four domains not present in expert_pairs.py:
  1. Security & Crypto          (pairs  1-20)
  2. Performance Debugging       (pairs 21-40)
  3. Cron & Automation           (pairs 41-60)
  4. Package Management          (pairs 61-80)

Commands reflect what a senior engineer with 10+ years of experience would
type — production-safe, properly quoted, idiomatic flag usage.
No pair duplicates expert_pairs.py content.
"""

PAIRS: list[tuple[str, str]] = [
    # =========================================================================
    # SECURITY & CRYPTO (20 pairs)
    # =========================================================================

    # openssl certificate operations
    (
        "generate a 4096-bit RSA private key",
        "openssl genrsa -out private.key 4096",
    ),
    (
        "create a certificate signing request from an existing key",
        "openssl req -new -key private.key -out request.csr -subj '/CN=example.com/O=MyOrg/C=US'",
    ),
    (
        "view the details of an x509 certificate",
        "openssl x509 -in cert.pem -noout -text",
    ),
    (
        "verify a certificate matches its private key",
        "diff <(openssl x509 -in cert.pem -pubkey -noout) <(openssl rsa -in private.key -pubout 2>/dev/null)",
    ),
    (
        "convert a PEM certificate to DER format",
        "openssl x509 -in cert.pem -outform DER -out cert.der",
    ),

    # GPG encrypt / decrypt / sign
    (
        "encrypt a file for a specific recipient with GPG",
        "gpg --encrypt --recipient user@example.com --output secret.gpg plaintext.txt",
    ),
    (
        "decrypt a GPG-encrypted file",
        "gpg --decrypt --output plaintext.txt secret.gpg",
    ),
    (
        "sign a file with your GPG key",
        "gpg --detach-sign --armor --output file.sig file.txt",
    ),
    (
        "verify a GPG detached signature",
        "gpg --verify file.sig file.txt",
    ),
    (
        "list all keys in your GPG keyring",
        "gpg --list-keys --keyid-format LONG",
    ),

    # SSH key management (agent, forwarding)
    (
        "generate an ed25519 SSH key with a comment",
        "ssh-keygen -t ed25519 -C 'user@host-$(date +%Y%m%d)' -f ~/.ssh/id_ed25519_new",
    ),
    (
        "add a private key to the SSH agent for the session",
        "ssh-add -t 3600 ~/.ssh/id_ed25519",
    ),
    (
        "list all identities loaded in the SSH agent",
        "ssh-add -l",
    ),
    (
        "copy your public key to a remote server",
        "ssh-copy-id -i ~/.ssh/id_ed25519.pub user@remote.host",
    ),
    (
        "connect to a host with agent forwarding enabled",
        "ssh -A user@bastion.example.com",
    ),

    # File integrity (shasum, md5)
    (
        "compute SHA-256 checksum of a file",
        "shasum -a 256 installer.pkg",
    ),
    (
        "verify a file against a published SHA-256 checksum",
        "echo 'abc123...  installer.pkg' | shasum -a 256 -c -",
    ),
    (
        "generate MD5 checksums for all files in a directory",
        "find . -type f -print0 | xargs -0 md5 -r 2>/dev/null | sort > checksums.md5",
    ),

    # chmod / chown patterns for security
    (
        "lock down SSH private key permissions",
        "chmod 600 ~/.ssh/id_ed25519 && chmod 700 ~/.ssh",
    ),
    (
        "recursively set correct web-root ownership and permissions",
        "find /var/www/html -type d -exec chmod 755 {} + && find /var/www/html -type f -exec chmod 644 {} +",
    ),

    # =========================================================================
    # PERFORMANCE DEBUGGING (20 pairs)
    # =========================================================================

    # strace / dtrace / dtruss
    (
        "trace all file-open syscalls made by a running process",
        "strace -p $(pgrep -n nginx) -e trace=openat,open 2>&1 | head -50",
    ),
    (
        "trace network syscalls of a new process invocation",
        "strace -e trace=network,socket -f ./server 2>&1 | head -100",
    ),
    (
        "summarise syscall counts and time for a command",
        "strace -c -f ./app 2>&1 | tail -20",
    ),
    (
        "trace file opens on macOS using dtruss",
        "sudo dtruss -f -t open_nocancel -p $(pgrep -n node) 2>&1 | head -50",
    ),

    # perf / flamegraph
    (
        "record a CPU perf profile for 10 seconds",
        "sudo perf record -F 99 -g -p $(pgrep app) -- sleep 10",
    ),
    (
        "generate a flamegraph from a perf.data recording",
        "sudo perf script | stackcollapse-perf.pl | flamegraph.pl > flamegraph.svg",
    ),
    (
        "show top CPU-consuming functions in perf report",
        "sudo perf report --stdio --sort=dso,symbol | head -40",
    ),

    # time and benchmark
    (
        "run a command three times and show real elapsed time each run",
        "for i in 1 2 3; do { time ./benchmark; } 2>&1 | grep real; done",
    ),
    (
        "measure wall clock and CPU time of a pipeline",
        "{ time (gzip -c largefile | wc -c); } 2>&1",
    ),
    (
        "benchmark two implementations and compare",
        "hyperfine --warmup 5 './impl_a input.dat' './impl_b input.dat' --export-markdown results.md",
    ),

    # memory profiling (valgrind, leaks on macOS)
    (
        "run a program under valgrind memcheck and show leak summary",
        "valgrind --leak-check=full --show-leak-kinds=all --track-origins=yes ./app 2>&1 | tail -30",
    ),
    (
        "profile heap allocations with valgrind massif",
        "valgrind --tool=massif --pages-as-heap=yes ./app && ms_print massif.out.* | head -60",
    ),
    (
        "check for memory leaks on macOS with leaks tool",
        "leaks --atExit -- ./app 2>&1 | grep 'leaks for'",
    ),
    (
        "run heap profiling with gperftools on Linux",
        "HEAPPROFILE=/tmp/heap.prof LD_PRELOAD=/usr/lib/libprofiler.so ./app",
    ),

    # I/O monitoring (iotop, iostat)
    (
        "show live disk I/O by process updated every second",
        "sudo iotop -o -b -n 5 -d 1 | tail -20",
    ),
    (
        "show per-device disk throughput every 2 seconds",
        "iostat -x 2 5 | grep -v '^$'",
    ),
    (
        "watch disk read/write speeds on macOS",
        "iostat -d -w 2 5",
    ),
    (
        "find which process is hammering disk I/O right now",
        "sudo iotop -o -P -b -n 1 | sort -k10 -rn | head -10",
    ),
    (
        "measure latency of disk operations with fio quick test",
        "fio --name=randread --ioengine=libaio --iodepth=16 --rw=randread --bs=4k --size=256M --runtime=10 --filename=/tmp/fio_test",
    ),

    # =========================================================================
    # CRON & AUTOMATION (20 pairs)
    # =========================================================================

    # crontab edit / list / remove
    (
        "open crontab for editing",
        "EDITOR=nano crontab -e",
    ),
    (
        "list all cron jobs for the current user",
        "crontab -l 2>/dev/null || echo 'no crontab for $USER'",
    ),
    (
        "remove all cron jobs for the current user",
        "crontab -r",
    ),
    (
        "back up current crontab before modifying it",
        "crontab -l > ~/crontab.bak.$(date +%Y%m%d) 2>/dev/null",
    ),
    (
        "schedule a script to run every day at 2:30 AM",
        "(crontab -l 2>/dev/null; echo '30 2 * * * /opt/scripts/daily.sh >> /var/log/daily.log 2>&1') | crontab -",
    ),
    (
        "run a job every 15 minutes and log output",
        "(crontab -l 2>/dev/null; echo '*/15 * * * * /opt/scripts/check.sh >> /var/log/check.log 2>&1') | crontab -",
    ),

    # systemd service management
    (
        "enable a systemd service to start on boot",
        "sudo systemctl enable --now myapp.service",
    ),
    (
        "disable a systemd service and stop it immediately",
        "sudo systemctl disable --now myapp.service",
    ),
    (
        "view the last 100 lines of a service journal",
        "journalctl -u myapp.service -n 100 --no-pager",
    ),
    (
        "create a minimal systemd unit file for a web service",
        "sudo tee /etc/systemd/system/myapp.service > /dev/null <<'EOF'\n[Unit]\nDescription=My Application\nAfter=network.target\n\n[Service]\nUser=appuser\nWorkingDirectory=/opt/myapp\nExecStart=/opt/myapp/bin/server\nRestart=always\nRestartSec=5\n\n[Install]\nWantedBy=multi-user.target\nEOF",
    ),

    # launchctl on macOS
    (
        "load and start a launchd plist agent immediately",
        "launchctl load -w ~/Library/LaunchAgents/com.example.myapp.plist",
    ),
    (
        "unload and stop a launchd agent",
        "launchctl unload -w ~/Library/LaunchAgents/com.example.myapp.plist",
    ),
    (
        "check if a launchd agent is running",
        "launchctl list | grep com.example.myapp",
    ),
    (
        "run a command every 5 minutes via a launchd plist",
        "cat > ~/Library/LaunchAgents/com.example.heartbeat.plist <<'EOF'\n<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n<plist version=\"1.0\"><dict>\n  <key>Label</key><string>com.example.heartbeat</string>\n  <key>ProgramArguments</key><array><string>/opt/scripts/heartbeat.sh</string></array>\n  <key>StartInterval</key><integer>300</integer>\n  <key>RunAtLoad</key><true/>\n</dict></plist>\nEOF\nlaunchctl load -w ~/Library/LaunchAgents/com.example.heartbeat.plist",
    ),

    # at / batch scheduling
    (
        "schedule a one-time job to run in 10 minutes",
        "echo '/opt/scripts/reindex.sh >> /tmp/reindex.log 2>&1' | at now + 10 minutes",
    ),
    (
        "list all pending at jobs",
        "atq",
    ),
    (
        "remove a pending at job by job number",
        "atrm 3",
    ),

    # watchdog / supervisor patterns
    (
        "start a supervisor-managed process and check its status",
        "supervisorctl start myapp && supervisorctl status myapp",
    ),
    (
        "tail supervisor log for a specific program",
        "supervisorctl tail -f myapp stderr",
    ),
    (
        "reload supervisor config and restart all programs",
        "supervisorctl reread && supervisorctl update && supervisorctl restart all",
    ),

    # =========================================================================
    # PACKAGE MANAGEMENT (20 pairs)
    # =========================================================================

    # brew advanced
    (
        "add a third-party Homebrew tap",
        "brew tap hashicorp/tap",
    ),
    (
        "install a GUI application with Homebrew Cask",
        "brew install --cask visual-studio-code",
    ),
    (
        "start a Homebrew-managed background service",
        "brew services start postgresql@16",
    ),
    (
        "stop and remove a Homebrew service from auto-start",
        "brew services stop redis && brew services cleanup",
    ),
    (
        "remove unused Homebrew downloads and old versions",
        "brew cleanup --prune=7 -s",
    ),
    (
        "upgrade all outdated Homebrew packages",
        "brew update && brew upgrade",
    ),

    # npm / yarn / pnpm
    (
        "install dependencies without modifying the lockfile",
        "npm ci",
    ),
    (
        "add a dev dependency with pnpm",
        "pnpm add -D typescript",
    ),
    (
        "run a package binary without installing it globally",
        "npx --yes tsx src/seed.ts",
    ),
    (
        "check which installed npm packages are outdated",
        "npm outdated --depth=0",
    ),
    (
        "list top-level npm packages only",
        "npm ls --depth=0",
    ),

    # pip / uv / pipx
    (
        "create an isolated virtual environment with uv and install deps",
        "uv venv .venv && uv pip install -r requirements.txt",
    ),
    (
        "install a Python CLI tool globally with pipx",
        "pipx install httpie",
    ),
    (
        "upgrade all pipx-installed tools",
        "pipx upgrade-all",
    ),
    (
        "sync project dependencies precisely from pyproject.toml with uv",
        "uv pip sync requirements/prod.txt",
    ),

    # apt / dnf
    (
        "install a package and its recommended dependencies on Debian",
        "sudo apt-get install -y --install-recommends git-lfs",
    ),
    (
        "search available packages matching a keyword on Red Hat",
        "dnf search 'postgresql'",
    ),
    (
        "show which package provides a specific file on Debian",
        "dpkg -S /usr/bin/psql",
    ),

    # version management (nvm, pyenv, rustup)
    (
        "install a specific Node.js version with nvm and use it",
        "nvm install 22 && nvm use 22 && nvm alias default 22",
    ),
    (
        "set a global Python version with pyenv",
        "pyenv install 3.13.0 && pyenv global 3.13.0",
    ),
    (
        "update the stable Rust toolchain and all components",
        "rustup update stable && rustup component add clippy rustfmt",
    ),
]

# Sanity check at import time
assert len(PAIRS) >= 80, f"Expected >= 80 pairs, got {len(PAIRS)}"
