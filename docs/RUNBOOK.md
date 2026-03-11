# NL2Shell — Execution Runbook

Quick-reference for executing each task. Copy-paste commands in order.

---

## T1: v1 Training [RUNNING on A100]
```bash
# Monitor
lecoder-cgpu run "tail -3 /content/train_output.log" 2>&1 | grep -o '[0-9]*/765'

# When done, check output
lecoder-cgpu run "grep 'TRAINING_COMPLETE' /content/train_output.log"
```

## T2: Verify v1 Model [AFTER T1]
```bash
# Check model exists on HuggingFace
curl -s https://huggingface.co/api/models/AryaYT/nl2shell-0.8b | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Model: {d[\"id\"]}, downloads: {d.get(\"downloads\",0)}')"

# Quick test with Ollama (if installed)
ollama run hf.co/AryaYT/nl2shell-0.8b "list all Python files"
```

## T4: v2 Training on H100 [AFTER T1]
```bash
# Close v1 session first
lecoder-cgpu sessions list
lecoder-cgpu sessions close <session-id>

# Start H100 session
lecoder-cgpu connect --gpu h100 --high-ram

# Copy v2 notebook as script (or upload notebook to Colab manually)
lecoder-cgpu copy nl2shell/nl2shell-v2-train.ipynb /content/nl2shell-v2-train.ipynb

# Alternative: copy train scripts and run
lecoder-cgpu copy nl2shell/prepare.py /content/prepare.py
lecoder-cgpu run "cd /content && jupyter nbconvert --to script nl2shell-v2-train.ipynb && python3 nl2shell-v2-train.py" --timeout 7200
```

## T5: Benchmark [AFTER T4]
```bash
# Copy benchmark script to Colab (reuse same session)
lecoder-cgpu copy nl2shell/benchmark.py /content/benchmark.py
lecoder-cgpu run "cd /content && python3 benchmark.py" --timeout 3600

# Download results
lecoder-cgpu run "cat /content/benchmark_results.json" > nl2shell/benchmark_results.json
```

## T6: Deploy HF Space [AFTER T1 or T4]
```bash
# Requires huggingface-cli installed locally
pip install huggingface-cli
bash nl2shell/deploy-space.sh

# Verify
open https://huggingface.co/spaces/AryaYT/nl2shell-demo
```

## T8: Paper [AFTER T5]
```bash
# Paper template at nl2shell/paper/nl2shell.tex
# Fill in [TBD] fields with benchmark results
# Compile locally or on Overleaf
cd nl2shell/paper && pdflatex nl2shell && bibtex nl2shell && pdflatex nl2shell && pdflatex nl2shell
```

## Cleanup
```bash
# Close all Colab sessions
lecoder-cgpu sessions list
lecoder-cgpu sessions close <session-id>
lecoder-cgpu sessions list  # verify zero
```
