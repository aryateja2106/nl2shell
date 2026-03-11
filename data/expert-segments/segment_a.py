"""
Expert-quality NL-to-shell pairs — Segment A.

Categories:
  1. Advanced stderr/stdout (20 pairs) — swap streams, PIPESTATUS, tee fanout, process substitution error handling
  2. Advanced git (20 pairs) — worktree, reflog, stash -p, log --grep, blame -L, submodules, sparse-checkout
  3. Kubernetes / Cloud (20 pairs) — kubectl patterns, AWS CLI one-liners, gcloud commands
  4. Database CLI (20 pairs) — psql, sqlite3, mysql, redis-cli, mongosh

No pair duplicates expert_pairs.py. Commands are real, single-line, senior-engineer quality.
"""

PAIRS: list[tuple[str, str]] = [
    # =========================================================================
    # ADVANCED STDERR / STDOUT (20 pairs)
    # =========================================================================
    # Stream swapping — 3>&1 1>&2 2>&3 idiom
    (
        "redirect only the stderr of a script through a grep filter while keeping stdout intact",
        "./build.sh 3>&1 1>&2 2>&3 | grep -i fail",
    ),
    (
        "swap stderr and stdout streams using a temporary file descriptor 3",
        "exec 3>&1; ./script.sh 2>&1 1>&3 3>&- | sed 's/^/ERR: /' >&2; exec 3>&-",
    ),
    # PIPESTATUS — capturing exit codes through a pipeline
    (
        "check exit code of first command in a pipe",
        'gzip < big.log | wc -c; echo "gzip exit: ${PIPESTATUS[0]}"',
    ),
    (
        "fail if any command in a pipeline fails",
        "set -o pipefail && make build | tee build.log",
    ),
    (
        "capture all pipeline exit codes after running",
        'cmd1 | cmd2 | cmd3; echo "exits: ${PIPESTATUS[*]}"',
    ),
    (
        "assert pipeline succeeded and print status array",
        "pg_dump mydb | gzip > mydb.sql.gz; [[ ${PIPESTATUS[0]} -eq 0 ]] || echo 'pg_dump failed'",
    ),
    # tee to multiple outputs simultaneously
    (
        "tee command output to two different files at once",
        "./deploy.sh | tee deploy.log >(grep ERROR > errors.log)",
    ),
    (
        "tee stdout to file while also sending to a log aggregator",
        "./app.sh 2>&1 | tee -a app.log | logger -t myapp",
    ),
    (
        "fan output to three consumers via process substitution",
        "cat access.log | tee >(grep 200 | wc -l > ok.txt) >(grep 500 | wc -l > err.txt) >/dev/null",
    ),
    (
        "tee stderr to a file while stdout continues to terminal",
        "{ ./run.sh 2>&1 1>&3 | tee errors.log 1>&2; } 3>&1",
    ),
    # Process substitution with error handling
    (
        "diff two command outputs and fail if they differ",
        "diff <(./expected.sh 2>/dev/null) <(./actual.sh 2>/dev/null) || exit 1",
    ),
    (
        "feed process substitution output into while loop",
        'while IFS= read -r line; do echo "got: $line"; done < <(kubectl get pods 2>/dev/null)',
    ),
    (
        "capture stderr of process substitution separately",
        "diff <(cmd1 2>cmd1_err.log) <(cmd2 2>cmd2_err.log)",
    ),
    # Named pipes / advanced redirect patterns
    (
        "write stdout to one file and stderr to another without shell builtins",
        "./app 1>out.log 2>err.log",
    ),
    (
        "redirect only fd 3 to a file for custom logging",
        "exec 3>debug.log; echo 'debug info' >&3; exec 3>&-",
    ),
    (
        "duplicate stdout to a log file using exec redirect",
        "exec > >(tee -a session.log) 2>&1",
    ),
    (
        "send stdout to file and stderr to a separate command",
        "./run.sh 2> >(grep -v DeprecationWarning >&2)",
    ),
    (
        "capture command output to variable while still printing it",
        "output=$(./check.sh | tee /dev/stderr)",
    ),
    (
        "print progress to stderr and final result to stdout",
        "{ echo 'working...' >&2; sleep 1; echo 'done'; }",
    ),
    (
        "redirect stdout to stderr for a single echo",
        "echo 'this goes to stderr' >&2",
    ),
    # =========================================================================
    # ADVANCED GIT (20 pairs)
    # =========================================================================
    # git worktree
    (
        "create a worktree for a hotfix branch without switching",
        "git worktree add ../hotfix-tree hotfix/critical-bug",
    ),
    (
        "list all active worktrees with their paths",
        "git worktree list --porcelain",
    ),
    (
        "remove a worktree and prune stale references",
        "git worktree remove ../hotfix-tree && git worktree prune",
    ),
    # git reflog
    (
        "find the commit hash before an accidental reset",
        "git reflog | grep 'reset\\|checkout' | head -20",
    ),
    (
        "recover a dropped stash using reflog",
        "git reflog | grep 'stash' | head -5",
    ),
    (
        "restore branch to state 3 moves ago via reflog",
        "git reset --hard HEAD@{3}",
    ),
    # git stash push -p (interactive partial stash)
    (
        "interactively stash only selected hunks",
        "git stash push -p -m 'partial wip: auth changes'",
    ),
    (
        "stash only a specific file",
        "git stash push -m 'wip: config only' -- config/settings.py",
    ),
    # Searching commit history with regex
    (
        "search commit messages for a pattern across all branches",
        "git log --all --oneline --grep='hotfix' --regexp-ignore-case",
    ),
    (
        "find all commits that added or removed a function name",
        "git log -S 'authenticate_user' --all --oneline --source",
    ),
    (
        "search commit diffs for a regex pattern",
        "git log -G 'password\\s*=' --oneline --all",
    ),
    # git blame with line range
    (
        "blame a specific line range in a file",
        "git blame -L 45,72 src/auth/jwt.ts",
    ),
    (
        "blame ignoring whitespace-only changes",
        "git blame -w -L 10,30 src/api/routes.py",
    ),
    # Show specific commit files / contents
    (
        "show the content of a file at a specific commit",
        "git show abc1234:src/config.ts",
    ),
    (
        "list all files that were changed in a specific commit",
        "git diff-tree --no-commit-id -r --name-only abc1234",
    ),
    # Submodule operations
    (
        "clone a repo and initialize all submodules recursively",
        "git clone --recurse-submodules https://github.com/org/repo.git",
    ),
    (
        "update all submodules to their latest tracked commit",
        "git submodule update --init --recursive --remote",
    ),
    (
        "show which submodule commit is checked out",
        "git submodule status --recursive",
    ),
    # Sparse checkout
    (
        "enable sparse checkout and fetch only a specific directory",
        "git sparse-checkout init --cone && git sparse-checkout set src/api",
    ),
    (
        "add another directory to an existing sparse checkout",
        "git sparse-checkout add docs/architecture",
    ),
    # =========================================================================
    # KUBERNETES / CLOUD (20 pairs)
    # =========================================================================
    # kubectl — get/describe/logs
    (
        "get all pods across all namespaces with node assignment",
        "kubectl get pods -A -o wide",
    ),
    (
        "follow logs of a crashing pod and restart on failure",
        "kubectl logs -f --previous deployment/api-server -n production",
    ),
    (
        "describe a failing pod to see events and status",
        "kubectl describe pod api-server-6d8f7b9-xkpqz -n production",
    ),
    (
        "exec into a running pod container",
        "kubectl exec -it deployment/api-server -n production -- /bin/sh",
    ),
    (
        "get all pods in CrashLoopBackOff state",
        "kubectl get pods -A --field-selector=status.phase=Running | grep CrashLoop",
    ),
    (
        "watch pod rollout status in real time",
        "kubectl rollout status deployment/api-server -n production --timeout=5m",
    ),
    (
        "port-forward a service to localhost for debugging",
        "kubectl port-forward svc/postgres 5432:5432 -n staging",
    ),
    (
        "get resource limits and requests for all pods in a namespace",
        "kubectl get pods -n production -o json | jq '.items[].spec.containers[].resources'",
    ),
    (
        "force delete a stuck terminating pod",
        "kubectl delete pod stuck-pod-xyz -n production --grace-period=0 --force",
    ),
    (
        "apply a manifest and wait for rollout to complete",
        "kubectl apply -f k8s/deployment.yaml && kubectl rollout status deployment/api-server -n production",
    ),
    # AWS CLI
    (
        "list all running EC2 instances with their IPs",
        "aws ec2 describe-instances --filters 'Name=instance-state-name,Values=running' --query 'Reservations[*].Instances[*].[InstanceId,PublicIpAddress,Tags[?Key==`Name`].Value|[0]]' --output table",
    ),
    (
        "tail CloudWatch logs for a Lambda function",
        "aws logs tail /aws/lambda/my-function --follow --format short",
    ),
    (
        "copy a file to S3 with server-side encryption",
        "aws s3 cp secrets.json s3://my-bucket/config/secrets.json --sse aws:kms",
    ),
    (
        "invoke a Lambda function and show the response",
        'aws lambda invoke --function-name my-function --payload \'{"key":"value"}\' /tmp/out.json && cat /tmp/out.json',
    ),
    (
        "get a secret value from Secrets Manager",
        "aws secretsmanager get-secret-value --secret-id prod/db/password --query SecretString --output text",
    ),
    # GCP gcloud
    (
        "list all Cloud Run services across all regions",
        "gcloud run services list --platform managed --format='table(name,region,status.url)'",
    ),
    (
        "stream Cloud Run logs in real time",
        "gcloud beta run services logs tail my-service --region us-central1",
    ),
    (
        "deploy a container image to Cloud Run",
        "gcloud run deploy my-service --image gcr.io/project/image:latest --region us-central1 --allow-unauthenticated",
    ),
    (
        "get the external IP of a GKE load balancer service",
        "gcloud compute forwarding-rules list --filter='name~my-service' --format='value(IPAddress)'",
    ),
    (
        "set a Cloud Run environment variable without redeploying image",
        "gcloud run services update my-service --set-env-vars DB_URL=postgres://host/db --region us-central1",
    ),
    # =========================================================================
    # DATABASE CLI (20 pairs)
    # =========================================================================
    # psql one-liners
    (
        "run a SQL query from the command line without interactive prompt",
        "psql -U myuser -d mydb -c 'SELECT count(*) FROM users WHERE active = true;'",
    ),
    (
        "export a table to CSV from psql",
        "psql -U myuser -d mydb -c '\\COPY users TO STDOUT WITH CSV HEADER' > users.csv",
    ),
    (
        "run a SQL file against a database non-interactively",
        "psql -U myuser -d mydb -f migrations/001_add_index.sql",
    ),
    (
        "show all table sizes in a PostgreSQL database",
        "psql -U myuser -d mydb -c 'SELECT relname, pg_size_pretty(pg_total_relation_size(oid)) FROM pg_class WHERE relkind=\\'r\\' ORDER BY pg_total_relation_size(oid) DESC LIMIT 20;'",
    ),
    (
        "list all running queries in PostgreSQL",
        "psql -U myuser -d mydb -c 'SELECT pid, now()-query_start AS duration, state, query FROM pg_stat_activity WHERE state != \\'idle\\' ORDER BY duration DESC;'",
    ),
    (
        "kill a long-running PostgreSQL query by pid",
        "psql -U myuser -d mydb -c 'SELECT pg_terminate_backend(12345);'",
    ),
    # sqlite3
    (
        "query a SQLite database file from the command line",
        "sqlite3 app.db 'SELECT * FROM sessions WHERE expires_at < datetime(\"now\");'",
    ),
    (
        "export SQLite table to CSV",
        "sqlite3 -header -csv app.db 'SELECT * FROM events ORDER BY created_at DESC LIMIT 1000;' > events.csv",
    ),
    (
        "show all tables in a SQLite database",
        "sqlite3 app.db '.tables'",
    ),
    (
        "check SQLite database integrity",
        "sqlite3 app.db 'PRAGMA integrity_check;'",
    ),
    (
        "run a vacuum on a SQLite database to reclaim space",
        "sqlite3 app.db 'VACUUM;'",
    ),
    # mysql
    (
        "run a MySQL query from the command line",
        "mysql -u root -p'$DB_PASS' mydb -e 'SELECT table_name, table_rows FROM information_schema.tables WHERE table_schema = database();'",
    ),
    (
        "dump a single MySQL table to SQL file",
        "mysqldump -u root -p'$DB_PASS' mydb users > users_backup.sql",
    ),
    (
        "import a SQL dump into MySQL",
        "mysql -u root -p'$DB_PASS' mydb < backup.sql",
    ),
    # redis-cli
    (
        "get all keys matching a pattern in Redis",
        "redis-cli --scan --pattern 'session:*' | head -20",
    ),
    (
        "flush all keys in a specific Redis database",
        "redis-cli -n 2 FLUSHDB",
    ),
    (
        "monitor live Redis commands in real time",
        "redis-cli MONITOR | grep -i 'set\\|get' | head -50",
    ),
    (
        "check Redis memory usage and eviction stats",
        "redis-cli INFO memory | grep -E 'used_memory_human|maxmemory_human|evicted_keys'",
    ),
    # mongosh
    (
        "count documents in a MongoDB collection from the shell",
        "mongosh mydb --eval 'db.users.countDocuments({active: true})'",
    ),
    (
        "export a MongoDB collection to JSON via mongosh",
        "mongosh mydb --eval 'JSON.stringify(db.events.find({},{_id:0}).toArray())' --quiet > events.json",
    ),
]

assert len(PAIRS) >= 80, f"Expected >= 80 pairs, got {len(PAIRS)}"
