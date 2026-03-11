#!/usr/bin/env bash
# Deploy NL2Shell demo to HuggingFace Spaces
# Usage: bash nl2shell/deploy-space.sh
set -euo pipefail

SPACE_REPO="AryaYT/nl2shell-demo"
HF_TOKEN="${HF_TOKEN:?Set HF_TOKEN env var}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Deploying NL2Shell to HuggingFace Spaces ==="

# 1. Create Space (Gradio SDK, free CPU tier)
echo "[1/4] Creating Space: $SPACE_REPO"
huggingface-cli repo create "$SPACE_REPO" --type space --space_sdk gradio 2>/dev/null || echo "  Space already exists"

# 2. Clone the Space repo
TMPDIR=$(mktemp -d)
echo "[2/4] Cloning Space to $TMPDIR"
cd "$TMPDIR"
git clone "https://huggingface.co/spaces/$SPACE_REPO" space
cd space

# 3. Copy files
echo "[3/4] Copying files..."
cp "$SCRIPT_DIR/SPACE_README.md" README.md
cp "$SCRIPT_DIR/app.py" app.py
cp "$SCRIPT_DIR/requirements.txt" requirements.txt

# 4. Push
echo "[4/4] Pushing to HuggingFace..."
git add -A
git commit -m "Deploy NL2Shell demo app" || echo "  No changes to commit"
git push "https://AryaYT:${HF_TOKEN}@huggingface.co/spaces/$SPACE_REPO" main

echo ""
echo "=== Deployed! ==="
echo "Space URL: https://huggingface.co/spaces/$SPACE_REPO"
echo ""

# Cleanup
rm -rf "$TMPDIR"
