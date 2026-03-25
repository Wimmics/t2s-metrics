# Installation Guide

## Prerequisites

- Python 3.12+
- `uv` (recommended) or `pip`
- SPARQL endpoint access if you run endpoint-based execution metrics
- Ollama only if you use LLM-based metrics

## Install from PyPI

```bash
pip install t2s-metrics
```

Check the CLI:

```bash
cli --help
```

## Install for development

Clone the repository, then install dependencies.

Using `uv`:

```bash
uv sync
uv sync --all-extras
```

Using `pip`:

```bash
pip install -e .
pip install -e ".[dev]"
```

## Build docs locally

From project root:

```bash
pip install -r docs/requirements.txt
sphinx-build -b html docs/ docs/_build/html
```

Open the generated site at `docs/_build/html/index.html`.
