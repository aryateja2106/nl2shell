"""
Expert-quality NL-to-shell pairs: segment D.

Categories:
  - CI/CD & DevOps (GitHub Actions CLI, Terraform, Ansible, Make/just, env vars)
  - Testing & Quality (pytest, coverage, lint, type checkers, benchmarks)
  - Data Wrangling (csvkit, jq advanced, yq, xsv, format conversion, base64)
  - Networking Advanced (tcpdump, iptables/nftables, DNS, curl timing, iperf3, mtr)

No overlap with expert_pairs.py (STDERR/STDOUT, human-readable, pipe mastery,
process substitution, xargs/find, macOS, one-liners, JSON/API, git, docker,
network/security basics, text processing, modern CLI, sysadmin, dev workflow).
"""

PAIRS: list[tuple[str, str]] = [
    # =========================================================================
    # CI/CD & DEVOPS (20 pairs)
    # =========================================================================
    # GitHub Actions CLI
    ("list recent GitHub Actions workflow runs", "gh run list --limit 20"),
    (
        "watch a GitHub Actions run in real time",
        "gh run watch $(gh run list --limit 1 --json databaseId -q '.[0].databaseId')",
    ),
    (
        "re-run all failed jobs in the latest workflow run",
        "gh run rerun --failed $(gh run list --limit 1 --json databaseId -q '.[0].databaseId')",
    ),
    (
        "view logs for a specific failed run",
        "gh run view --log-failed $(gh run list --limit 1 --json databaseId -q '.[0].databaseId')",
    ),
    ("list all workflow files in a repo", "gh workflow list"),
    (
        "manually trigger a workflow with an input",
        "gh workflow run deploy.yml -f environment=staging",
    ),
    ("disable a GitHub Actions workflow", "gh workflow disable build.yml"),
    # Terraform CLI
    ("initialize terraform and upgrade providers", "terraform init -upgrade"),
    ("plan terraform changes and save to file", "terraform plan -out=tfplan.binary"),
    ("apply a saved terraform plan", "terraform apply tfplan.binary"),
    ("destroy specific terraform resource", "terraform destroy -target=aws_instance.web"),
    ("show current terraform state summary", "terraform state list"),
    (
        "import an existing resource into terraform state",
        "terraform import aws_s3_bucket.assets my-bucket-name",
    ),
    ("format all terraform files in place", "terraform fmt -recursive"),
    # Ansible ad-hoc commands
    ("ping all hosts in inventory", "ansible all -m ping -i inventory.ini"),
    (
        "run ad-hoc shell command on a host group",
        "ansible webservers -m shell -a 'systemctl status nginx' -i inventory.ini",
    ),
    (
        "copy a file to all remote hosts",
        "ansible all -m copy -a 'src=./app.conf dest=/etc/app/app.conf' -i inventory.ini --become",
    ),
    # Make/just patterns
    (
        "list all available make targets",
        "make -qp | awk -F':' '/^[a-zA-Z0-9][^$#\\/\\t=]*:([^=]|$)/ {split($1,A,/ /); for(i in A) print A[i]}' | sort -u",
    ),
    ("run just recipe with dry-run to preview commands", "just --dry-run deploy"),
    # Environment variable management for CI
    ("export all variables from a .env file", "set -a && source .env && set +a"),
    # =========================================================================
    # TESTING & QUALITY (20 pairs)
    # =========================================================================
    # pytest patterns
    ("run only tests marked as slow", "pytest -m slow -v"),
    ("run tests matching a keyword expression", "pytest -k 'auth and not admin' -v"),
    (
        "run a single test function by node ID",
        "pytest tests/test_api.py::test_login_returns_token -v",
    ),
    ("run tests in parallel across 4 workers", "pytest -n 4"),
    ("show the 10 slowest tests after a run", "pytest --durations=10"),
    ("stop on first failure and enter debugger", "pytest -x --pdb"),
    ("regenerate all pytest snapshots", "pytest --snapshot-update"),
    ("run tests and emit junit XML for CI", "pytest --junitxml=test-results.xml"),
    # Coverage commands
    (
        "run tests with coverage and show missing lines",
        "pytest --cov=src --cov-report=term-missing",
    ),
    ("fail the build if coverage drops below 80%", "pytest --cov=src --cov-fail-under=80"),
    (
        "generate an HTML coverage report",
        "pytest --cov=src --cov-report=html && open htmlcov/index.html",
    ),
    (
        "show coverage diff against main branch",
        "coverage run -m pytest && coverage xml && diff-cover coverage.xml --compare-branch=main",
    ),
    # Lint runner patterns
    ("run ruff with auto-fix on entire project", "ruff check . --fix"),
    (
        "run eslint on staged files only",
        "git diff --cached --name-only --diff-filter=ACM | grep '\\.ts$' | xargs eslint",
    ),
    (
        "run clippy on all targets treating warnings as errors",
        "cargo clippy --all-targets -- -D warnings",
    ),
    (
        "lint all Python files and show first error only",
        "ruff check . --select E,W --quiet | head -1",
    ),
    # Type checker invocations
    (
        "check types across the whole monorepo with pyright",
        "pyright --outputjson 2>/dev/null | jq '.summary'",
    ),
    ("run mypy in strict mode on a module", "mypy --strict src/auth.py"),
    # Benchmark runners
    (
        "run criterion benchmarks and open HTML report",
        "cargo bench && open target/criterion/report/index.html",
    ),
    (
        "compare benchmark results against baseline",
        "hyperfine --warmup 5 --export-markdown bench.md './cmd_old' './cmd_new'",
    ),
    # =========================================================================
    # DATA WRANGLING (20 pairs)
    # =========================================================================
    # csvkit/csvtool
    ("show column names and types of a CSV file", "csvstat --names data.csv"),
    (
        "filter CSV rows where column value exceeds threshold",
        "csvgrep -c revenue -m '' data.csv | csvsort -c revenue -r | head -20",
    ),
    ("join two CSV files on a shared column", "csvjoin -c id users.csv orders.csv"),
    ("convert CSV to JSON array", "csvjson data.csv"),
    ("count rows in a CSV excluding header", "csvstat -c 1 --count data.csv | tail -1"),
    # jq advanced (multiple filters, conditionals)
    (
        "flatten nested JSON array and extract unique values",
        "jq '[.[].tags[]] | unique' data.json",
    ),
    (
        "group JSON array by a field and count",
        "jq 'group_by(.status) | map({status: .[0].status, count: length})' records.json",
    ),
    (
        "transform JSON with conditional field renaming",
        "jq '[.[] | {id, name: (.fullName // .name), active: (.status == \"enabled\")}]' users.json",
    ),
    (
        "merge JSON objects from two files at the key level",
        "jq -n --slurpfile a a.json --slurpfile b b.json '$a[0] * $b[0]'",
    ),
    (
        "extract nested paths that match a pattern",
        'jq \'.. | strings | select(test("error"; "i"))\' response.json',
    ),
    # yq for YAML
    ("read a nested YAML value by path", "yq '.spec.replicas' deployment.yaml"),
    ("set a YAML field in place", "yq -i '.spec.replicas = 3' deployment.yaml"),
    (
        "merge two YAML files, second overrides first",
        "yq eval-all 'select(fileIndex == 0) * select(fileIndex == 1)' base.yaml override.yaml",
    ),
    ("convert a YAML file to JSON", "yq -o=json config.yaml"),
    # xsv for fast CSV
    ("get summary statistics for all columns with xsv", "xsv stats data.csv | xsv table"),
    ("sort a large CSV by a numeric column descending", "xsv sort -s revenue -R data.csv"),
    ("select specific columns from a CSV with xsv", "xsv select id,name,email data.csv"),
    # Data format conversion and base64
    (
        "convert JSON to YAML using python",
        'python3 -c "import sys, json, yaml; yaml.dump(json.load(sys.stdin), sys.stdout, default_flow_style=False)" < data.json',
    ),
    ("base64 encode a file and copy to clipboard", "base64 < secret.key | tr -d '\\n' | pbcopy"),
    (
        "base64 decode a string and write to file",
        "echo 'SGVsbG8gV29ybGQ=' | base64 --decode > output.txt",
    ),
    # =========================================================================
    # NETWORKING ADVANCED (20 pairs)
    # =========================================================================
    # tcpdump patterns
    (
        "capture packets on port 443 and write to pcap file",
        "tcpdump -i eth0 -n 'tcp port 443' -w capture.pcap",
    ),
    (
        "capture DNS queries and show hostnames",
        "tcpdump -i any -n 'udp port 53' -l 2>/dev/null | grep -oP 'A\\? \\K[^ ]+'",
    ),
    (
        "watch HTTP POST requests in real time",
        "tcpdump -i eth0 -A -s 0 'tcp port 80 and (tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x504f5354)' 2>/dev/null",
    ),
    (
        "capture packets between two specific hosts",
        "tcpdump -i eth0 -n 'host 10.0.0.1 and host 10.0.0.2' -w host-pair.pcap",
    ),
    # iptables/nftables rules
    (
        "allow established and related connections in iptables",
        "iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT",
    ),
    (
        "rate-limit incoming SSH connections",
        "iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m limit --limit 3/min --limit-burst 3 -j ACCEPT",
    ),
    (
        "list nftables ruleset",
        "nft list ruleset",
    ),
    (
        "block outgoing traffic to a specific IP with nftables",
        "nft add rule ip filter output ip daddr 203.0.113.0/24 drop",
    ),
    # DNS debugging
    (
        "query MX records for a domain",
        "dig MX example.com +short",
    ),
    (
        "check DNSSEC validation for a domain",
        "dig +dnssec example.com",
    ),
    (
        "trace the full DNS resolution chain",
        "dig +trace example.com",
    ),
    (
        "query all DNS record types for a domain",
        "dig ANY example.com @8.8.8.8",
    ),
    # HTTP debugging with curl timing
    (
        "measure full HTTP request timing breakdown",
        "curl -so /dev/null -w 'namelookup:%{time_namelookup}s connect:%{time_connect}s starttransfer:%{time_starttransfer}s total:%{time_total}s\\n' https://example.com",
    ),
    (
        "check which TLS version and cipher a server uses",
        "curl -svo /dev/null https://example.com 2>&1 | grep -E 'SSL|TLS|cipher'",
    ),
    (
        "send request with custom Host header for vhost testing",
        "curl -sf -H 'Host: staging.example.com' http://10.0.0.5/healthz",
    ),
    (
        "follow redirects and print each redirect URL",
        "curl -sIL https://short.link/abc 2>&1 | grep -i 'location:'",
    ),
    # Bandwidth testing with iperf3
    (
        "run iperf3 TCP throughput test to a server",
        "iperf3 -c 192.168.1.10 -t 10 -P 4",
    ),
    (
        "run iperf3 UDP bandwidth test at 100 Mbps",
        "iperf3 -c 192.168.1.10 -u -b 100M -t 10",
    ),
    # mtr/traceroute patterns
    (
        "run mtr in report mode and show 100 cycles",
        "mtr --report --report-cycles 100 --no-dns 8.8.8.8",
    ),
    (
        "traceroute using TCP SYN instead of UDP for firewalled paths",
        "traceroute -T -p 443 example.com",
    ),
]

# Sanity check at import time
assert len(PAIRS) >= 80, f"Expected >= 80 pairs, got {len(PAIRS)}"
