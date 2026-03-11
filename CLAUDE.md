# NL2Shell

Natural Language to Shell Command translation — fine-tuned Qwen3.5-0.8B.

## Build & Lint
```bash
uv sync --group dev          # install dev tools
ruff check .                 # lint
ruff format .                # format
ty check .                   # type check
```

## Training (requires GPU)
```bash
uv sync --group train
python train.py              # QLoRA fine-tune on NL2Bash
python benchmark.py          # evaluate on 606 test examples
```

## Demo
```bash
uv sync --group demo
python app.py                # launch Gradio interface
```

## Conventions
- Python 3.10+, ruff for lint/format, ty for type checking
- All HF tokens via `HF_TOKEN` env var — never hardcode
- Conventional commits: `type(scope): description`
- Scripts are standalone — no package imports between them
