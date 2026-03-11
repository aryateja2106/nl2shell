"""Segment I — Package Manager & Project Workflows (100 pairs)"""

PAIRS: list[tuple[str, str]] = [
    # =========================================================================
    # HOMEBREW (20 pairs)
    # =========================================================================
    # Install / uninstall / upgrade
    ("install the wget formula with homebrew", "brew install wget"),
    ("uninstall the imagemagick formula", "brew uninstall imagemagick"),
    ("upgrade a specific formula to the latest version", "brew upgrade ripgrep"),
    ("upgrade all outdated homebrew packages at once", "brew upgrade"),
    ("what homebrew packages are outdated", "brew outdated"),
    # Cleanup
    ("remove old versions of all homebrew formulas", "brew cleanup"),
    ("clean up homebrew packages older than 7 days", "brew cleanup --prune=7"),
    (
        "see how much disk space homebrew cleanup would free without deleting anything",
        "brew cleanup -n",
    ),
    # Search / info
    ("search homebrew for a formula matching httpie", "brew search httpie"),
    ("show info and homepage for the jq formula", "brew info jq"),
    ("list all installed homebrew casks", "brew list --cask"),
    # Maintenance
    ("reinstall a broken or corrupted homebrew formula", "brew reinstall node"),
    ("check homebrew for configuration issues", "brew doctor"),
    ("update homebrew itself and the formula lists", "brew update"),
    ("pin a formula so it does not get upgraded", "brew pin python@3.12"),
    ("unpin a formula to allow upgrades again", "brew unpin python@3.12"),
    # Taps / dependencies
    ("tap the homebrew-cask-fonts repository", "brew tap homebrew/cask-fonts"),
    ("show which installed packages depend on openssl", "brew uses --installed openssl"),
    ("list all direct dependencies of the ffmpeg formula", "brew deps ffmpeg"),
    ("show the full dependency tree for a formula", "brew deps --tree ffmpeg"),
    # =========================================================================
    # npm / pnpm / bun (25 pairs)
    # =========================================================================
    # Installing / managing dependencies
    ("install all project dependencies with bun", "bun install"),
    ("add a package as a dev dependency using bun", "bun add -d vitest"),
    ("add a runtime dependency to the project", "bun add zod"),
    ("remove a package from the project", "bun remove lodash"),
    (
        "clean node_modules and reinstall everything from scratch",
        "rm -rf node_modules && bun install",
    ),
    # Running scripts
    ("start the dev server", "bun dev"),
    ("run the build script", "bun run build"),
    ("run tests with bun", "bun test"),
    ("run a specific npm script by name", "bun run lint"),
    ("check what scripts are available in this project", "jq '.scripts' package.json"),
    # Outdated / auditing
    ("check for outdated packages in this project", "npm outdated"),
    ("audit the project for known security vulnerabilities", "npm audit"),
    ("automatically fix low-severity vulnerabilities", "npm audit fix"),
    # Global packages
    ("list globally installed npm packages at top level", "npm list -g --depth=0"),
    ("install a tool globally with npm", "npm install -g typescript"),
    ("uninstall a globally installed npm tool", "npm uninstall -g create-react-app"),
    # Querying / introspection
    ("find which installed package provides the jest binary", "npm ls jest"),
    ("check the version of a locally installed package", "jq '.dependencies.react' package.json"),
    ("show the full resolved version of every dependency", "bun pm ls"),
    ("print the bin path for a locally installed tool", "bun pm bin"),
    # npx / one-off tools
    ("run a one-off npx tool without installing it", "npx cowsay hello"),
    ("check the bundle size of a package without installing it", "npx bundlephobia-cli axios"),
    (
        "scaffold a new vite project without globally installing vite",
        "npx create-vite@latest my-app",
    ),
    ("generate a new next.js app using npx", "npx create-next-app@latest my-app"),
    ("run prettier on all typescript files as a one-off", "npx prettier --write '**/*.ts'"),
    # =========================================================================
    # CARGO / RUST (15 pairs)
    # =========================================================================
    ("build the rust project in release mode", "cargo build --release"),
    ("check the rust project for errors without producing a binary", "cargo check"),
    ("run clippy lints across all targets", "cargo clippy --all-targets"),
    ("format all rust source files", "cargo fmt"),
    ("add a crate dependency to the project", "cargo add serde --features derive"),
    ("remove a crate dependency from the project", "cargo remove serde"),
    ("run a specific test by name", "cargo test test_parse_config"),
    ("run all tests and show output even for passing tests", "cargo test -- --nocapture"),
    ("show the full dependency tree for this rust project", "cargo tree"),
    ("update all dependencies to their latest compatible versions", "cargo update"),
    ("publish the crate to crates.io", "cargo publish"),
    ("run the project binary with arguments", "cargo run -- --help"),
    ("generate and open the documentation for this crate", "cargo doc --open"),
    ("check what features are available on a crate", "cargo add tokio --features full --dry-run"),
    ("audit rust dependencies for known security vulnerabilities", "cargo audit"),
    # =========================================================================
    # uv / PYTHON (15 pairs)
    # =========================================================================
    ("create a new python project with uv", "uv init my-project"),
    ("add a python package dependency with uv", "uv add httpx"),
    ("add a dev-only python dependency", "uv add --dev pytest"),
    ("remove a python package from the project", "uv remove httpx"),
    ("create a virtual environment in the current directory", "uv venv"),
    ("sync all dependencies from the lockfile", "uv sync"),
    ("run a python script inside the uv-managed environment", "uv run python script.py"),
    ("run a tool without installing it globally using uvx", "uvx ruff check ."),
    ("install a python tool globally with pipx", "pipx install black"),
    ("upgrade a globally installed pipx tool", "pipx upgrade ruff"),
    ("list all pipx-managed tools", "pipx list"),
    ("show the resolved dependency tree for a uv project", "uv tree"),
    ("lock the python dependencies without installing", "uv lock"),
    ("run pytest through uv", "uv run pytest"),
    ("show which python interpreter uv is using", "uv python pin"),
    # =========================================================================
    # PROJECT DETECTION & CONTEXT-AWARE (15 pairs)
    # =========================================================================
    (
        "what kind of project is this",
        "ls package.json Cargo.toml pyproject.toml Makefile go.mod 2>/dev/null",
    ),
    (
        "show project dependencies based on whatever system this uses",
        "{ [ -f package.json ] && jq '.dependencies' package.json; } || { [ -f Cargo.toml ] && cargo tree; } || { [ -f pyproject.toml ] && uv tree; }",
    ),
    (
        "lint the project using whichever linter is configured",
        "{ [ -f package.json ] && bun run lint; } || { [ -f Cargo.toml ] && cargo clippy --all-targets; } || { [ -f pyproject.toml ] && uvx ruff check .; }",
    ),
    (
        "check if the project builds successfully",
        "{ [ -f package.json ] && bun run build; } || { [ -f Cargo.toml ] && cargo build; } || { [ -f pyproject.toml ] && uv sync; }",
    ),
    (
        "run the project's test suite using the appropriate tool",
        "{ [ -f package.json ] && bun test; } || { [ -f Cargo.toml ] && cargo test; } || { [ -f pyproject.toml ] && uv run pytest; }",
    ),
    ("show the git remote URLs for this repository", "git remote -v"),
    ("what branch am I currently on", "git branch --show-current"),
    ("show the last 10 commits in this repo", "git log --oneline -10"),
    ("show uncommitted changes in this project", "git status --short"),
    (
        "show what changed since the last release tag",
        "git log $(git describe --tags --abbrev=0)..HEAD --oneline",
    ),
    ("open the project in the finder", "open ."),
    (
        "count total lines of source code in this project",
        "find . -type f \\( -name '*.ts' -o -name '*.rs' -o -name '*.py' \\) -not -path '*/node_modules/*' -not -path '*/.venv/*' | xargs wc -l | tail -1",
    ),
    ("show the size of node_modules", "du -sh node_modules 2>/dev/null || echo 'no node_modules'"),
    (
        "check the node version required by this project",
        "jq '.engines.node' package.json 2>/dev/null || cat .nvmrc 2>/dev/null || cat .node-version 2>/dev/null",
    ),
    ("show the current bun version", "bun --version"),
    # =========================================================================
    # DEPENDENCY MANAGEMENT (10 pairs)
    # =========================================================================
    ("find unused dependencies in a typescript project", "npx depcheck"),
    ("check for security vulnerabilities in npm packages", "npm audit"),
    ("check for security vulnerabilities in rust dependencies", "cargo audit"),
    (
        "generate a lockfile for the current bun project without installing",
        "bun install --frozen-lockfile --dry-run",
    ),
    (
        "show what changed in dependencies since the last lockfile commit",
        "git diff HEAD -- bun.lockb package.json Cargo.lock uv.lock",
    ),
    (
        "check if the lockfile is up to date without modifying anything",
        "bun install --frozen-lockfile",
    ),
    ("deduplicate dependencies in the npm lockfile", "npm dedupe"),
    ("show all transitive python dependencies including versions", "uv tree --depth 5"),
    (
        "find which dependency introduced a vulnerable package",
        "npm ls --all 2>/dev/null | grep -i <pkg>",
    ),
    ("check if a rust crate has any yanked versions in use", "cargo audit --deny yanked"),
]
