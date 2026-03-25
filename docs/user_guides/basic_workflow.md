# Basic Workflow Guide

This guide covers the most common workflow: prepare input, run metrics, and inspect results.

## 1. Prepare JSONL input

Each line must include:

- `id`
- `golden`
- `generated`
- `order_matters`

Example:

```json
{"id": "ck25:1-en", "golden": "SELECT ...", "generated": "SELECT ...", "order_matters": false}
```

## 2. Pick an execution backend

- Local KG file with `--execution_backend_graph_path`
- SPARQL endpoint with `--execution_backend_endpoint_url`

## 3. Run from CLI

```bash
cli run \
  -d ck25 \
  -j ./datasets/ck25/eval/ \
  -m query_exact_match answerset_f1 query_execution \
  -ee http://localhost:8886/ \
  -p -v
```

## 4. Run from Python

```python
from t2smetrics import run_experiments

run_experiments.run(
    dataset="example",
    jsonl_evals=["./datasets/example/eval/example.jsonl"],
    metrics_list=["query_exact_match", "answerset_f1", "query_execution"],
    execution_backend_graph_path="./datasets/example/kg/example.ttl",
    verbose=True,
)
```

## 5. Inspect result files

Results are exported as JSON under the dataset result folder, for example:

- `datasets/ck25/results/ck25-YYYYMMDD-HHMMSS.json`
