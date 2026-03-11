"""Segment K — Modern CLI Tools & Advanced Shell Patterns (100 pairs)"""

PAIRS: list[tuple[str, str]] = [
    # =========================================================================
    # RIPGREP / rg (15 pairs)
    # =========================================================================
    ("search for TODO in all TypeScript files", "rg TODO -t ts"),
    ("find all function definitions in JavaScript files", "rg 'function \\w+' -t js"),
    ("search for a pattern ignoring case", "rg -i pattern ."),
    ("search and show only filenames with matches", "rg -l pattern ."),
    ("search with 3 lines of context around each match", "rg -C3 pattern ."),
    ("count matches per file", "rg -c pattern ."),
    ("search for pattern in the src directory only", "rg pattern src/"),
    ("search excluding node_modules", "rg pattern -g '!node_modules'"),
    ("find all imports of a specific module in TypeScript", "rg 'import.*from.*module' -t ts"),
    (
        "replace text across all files matching a pattern",
        "rg pattern -l | xargs sed -i '' 's/old/new/g'",
    ),
    ("search for pattern and show only the matching portion", "rg -o 'https?://[^\\s]+' ."),
    ("search across hidden files and directories", "rg --hidden pattern ."),
    ("search for multiline patterns", "rg -U 'start.*\\nend' ."),
    ("show files that do NOT match a pattern", "rg --files-without-match pattern ."),
    ("search with a fixed string instead of regex", "rg -F 'literal.string' ."),
    # =========================================================================
    # fd (15 pairs)
    # =========================================================================
    ("find all TypeScript files recursively", "fd -e ts"),
    ("find files modified in the last hour", "fd --changed-within 1h"),
    ("find and delete all .DS_Store files", "fd -H .DS_Store -x rm"),
    ("find files larger than 10 megabytes", "fd -t f -S +10m"),
    ("find files matching a name pattern", "fd pattern"),
    ("find directories only matching a name", "fd -t d name"),
    ("find Python files and count their lines", "fd -e py -x wc -l"),
    ("find files excluding node_modules and .git", "fd pattern -E node_modules -E .git"),
    ("find all files owned by current user", "fd -t f --owner $(whoami)"),
    ("find executable files", "fd -t x"),
    ("find symlinks in a directory", "fd -t l"),
    (
        "find files modified between two dates",
        "fd --changed-after 2025-01-01 --changed-before 2025-06-01",
    ),
    (
        "find all json files and pretty-print them",
        "fd -e json -x sh -c 'echo \"=== {} ===\"; cat {}'",
    ),
    ("find empty files", "fd -t f --size 0"),
    ("find and open all markdown files in editor", "fd -e md -x $EDITOR"),
    # =========================================================================
    # eza (10 pairs)
    # =========================================================================
    ("list files with details and icons", "eza -la --icons"),
    ("show directory tree two levels deep", "eza --tree -L 2"),
    ("list files sorted by size", "eza -la --sort=size"),
    ("list only directories", "eza -D"),
    ("show git status alongside file list", "eza -la --git"),
    ("list files sorted by modification time", "eza -la --sort=modified"),
    ("show file tree with git status three levels deep", "eza --tree --git -L 3"),
    ("list all files including hidden ones with icons", "eza -la --icons --all"),
    ("show file sizes in bytes", "eza -la --bytes"),
    ("list files with their inode numbers", "eza -la --inode"),
    # =========================================================================
    # fzf / FUZZY FINDING (15 pairs)
    # =========================================================================
    ("fuzzy find a file and open it in editor", "fd -t f | fzf | xargs $EDITOR"),
    ("fuzzy search and switch git branches", "git branch | fzf | xargs git checkout"),
    ("interactively kill a process by name", "ps aux | fzf | awk '{print $2}' | xargs kill"),
    (
        "fuzzy search command history and run selection",
        "history | fzf | awk '{$1=\"\"; print}' | bash",
    ),
    (
        "preview files with syntax highlighting while searching",
        "fd -t f | fzf --preview 'bat --color=always {}'",
    ),
    (
        "fuzzy search docker containers and tail logs",
        "docker ps --format '{{.Names}}' | fzf | xargs docker logs -f",
    ),
    ("interactive git log with commit preview", "git log --oneline | fzf --preview 'git show {1}'"),
    ("fuzzy select a directory and cd into it", 'fd -t d | fzf | read -r dir && cd "$dir"'),
    ("fuzzy find and checkout a git tag", "git tag | fzf | xargs git checkout"),
    (
        "fuzzy select an npm script and run it",
        "jq -r '.scripts | keys[]' package.json | fzf | xargs bun run",
    ),
    (
        "fuzzy pick a running docker container and exec into it",
        "docker ps --format '{{.Names}}' | fzf | xargs -I{} docker exec -it {} bash",
    ),
    ("fuzzy select a file and copy its path to clipboard", "fd -t f | fzf | pbcopy"),
    ("fuzzy search environment variables", "env | fzf"),
    (
        "fuzzy select a git stash and apply it",
        "git stash list | fzf | awk -F: '{print $1}' | xargs git stash apply",
    ),
    (
        "fuzzy find and delete a git branch",
        "git branch | grep -v '\\*' | fzf | xargs git branch -d",
    ),
    # =========================================================================
    # zoxide (5 pairs)
    # =========================================================================
    ("jump to the projects folder", "z projects"),
    ("jump to the most used directory matching a pattern", "z pattern"),
    ("open interactive directory picker", "zi"),
    ("add current directory to zoxide database", "zoxide add ."),
    ("list the ten most visited directories", "zoxide query -l | head -10"),
    # =========================================================================
    # PIPING & COMPOSITION (20 pairs)
    # =========================================================================
    ("find the ten largest files recursively", "fd -t f -x du -b | sort -rn | head -10"),
    (
        "count lines of code across TypeScript Python and Rust files",
        "fd -e ts -e py -e rs -x wc -l | sort -rn",
    ),
    (
        "show unique error types from a log file",
        "rg ERROR app.log | awk -F: '{print $NF}' | sort -u",
    ),
    (
        "find files with duplicate names across directories",
        "fd -t f | awk -F/ '{print $NF}' | sort | uniq -d",
    ),
    (
        "show top five most common HTTP status codes in access log",
        "awk '{print $9}' access.log | sort | uniq -c | sort -rn | head -5",
    ),
    (
        "fetch JSON from an API and format as an aligned table",
        "curl -s https://api.example.com/data | jq -r '.[] | [.name, .value] | @tsv' | column -t",
    ),
    (
        "watch source directory for changes and re-run tests",
        "fswatch -o src/ | xargs -n1 -I{} bun test",
    ),
    ("find all TODOs and format them as a markdown checklist", "rg TODO -n | sed 's/^/- [ ] /'"),
    ("extract all URLs from a file", "rg -o 'https?://[^\\s]+' file.txt"),
    ("show current disk usage percentage for root", "df -h / | awk 'NR==2{print $5}'"),
    ("list all processes sorted by memory usage", "ps aux | sort -rk 4 | head -10"),
    (
        "tail logs and highlight ERROR lines in red",
        "tail -f app.log | rg --passthru --color=always ERROR",
    ),
    ("find the most recently modified file in a directory", "fd -t f | xargs ls -t | head -1"),
    (
        "batch rename files replacing spaces with underscores",
        'fd -t f -e txt | xargs -I{} bash -c \'mv "$0" "${0// /_}"\' {}',
    ),
    (
        "count the number of each file extension in a project",
        "fd -t f | awk -F. '{print $NF}' | sort | uniq -c | sort -rn",
    ),
    (
        "show git diff stats piped through bat for syntax highlighting",
        "git diff --stat | bat -l diff",
    ),
    ("find all TODO FIXME and HACK comments", "rg 'TODO|FIXME|HACK' -t ts -t py -t rs"),
    ("list all npm dependencies with their versions as JSON", "jq '.dependencies' package.json"),
    ("search for a pattern across all git commits", "git log --all -p | rg pattern"),
    (
        "show the ten largest directories in the current path",
        "du -sh */ 2>/dev/null | sort -rh | head -10",
    ),
    # =========================================================================
    # PROCESS SUBSTITUTION & ADVANCED BASH (10 pairs)
    # =========================================================================
    ("diff the output of two commands", "diff <(command1) <(command2)"),
    ("compare file listings between two directories", "diff <(ls dir1) <(ls dir2)"),
    ("combine head of one file with tail of another", "cat <(head -20 file1) <(tail -20 file2)"),
    ("open the first file matching a pattern in the editor", "vim $(fd -t f pattern | head -1)"),
    ("run two commands in parallel and wait for both", "command1 & command2 & wait"),
    (
        "source env file if it exists otherwise warn",
        "test -f .env && source .env || echo 'no .env found'",
    ),
    ("feed two sorted files into a join operation", "join <(sort file1) <(sort file2)"),
    (
        "run a command for each line of a variable",
        'while IFS= read -r line; do echo "$line"; done <<< "$multiline_var"',
    ),
    (
        "check if a command exists before running it",
        "command -v rg &>/dev/null && rg TODO . || grep -r TODO .",
    ),
    ("time a command and print elapsed seconds", "time (bun test 2>&1) 2>&1 | tail -1"),
    # =========================================================================
    # just / TASK RUNNER (10 pairs)
    # =========================================================================
    ("list all available just recipes", "just --list"),
    ("run the default just recipe", "just"),
    ("run a specific just recipe", "just recipe-name"),
    ("run a just recipe with arguments", "just deploy staging"),
    ("show a recipe definition without running it", "just --show recipe-name"),
    ("run a recipe from a specific justfile", "just -f path/to/justfile recipe"),
    ("check which justfile would be used", "just --justfile"),
    ("run just with verbose output for debugging", "just --verbose recipe-name"),
    ("evaluate and print a just variable", "just --evaluate var_name"),
    ("choose a recipe interactively from a menu", "just --choose"),
]
