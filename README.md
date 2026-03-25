# T2S-Metrics

<div align="center">
<br>

<img src="https://raw.githubusercontent.com/Wimmics/t2s-metrics/main/img/logo.png" width="50%" style="border-radius: 5px;" alt="t2s-metrics logo">

</div>

<p align="center">
    <em>A small evaluation toolkit for text-to-SPARQL systems. It runs a configurable set
of metrics over JSONL datasets and can execute queries against local RDF files or
SPARQL endpoints.</em>
</p>

<p align="center">
    <a href="LICENSES"><img src="https://img.shields.io/badge/License-AGPL%20v3-blue" alt="LICENSES"></a>
    <a href="https://pypi.org/project/t2s-metrics"><img src="https://img.shields.io/pypi/v/t2s-metrics" alt="PyPI"></a>
    <a href="https://pypi.org/project/t2s-metrics/"><img src="https://img.shields.io/pypi/dm/t2s-metrics" alt="Downloads"></a>
    <a href="https://doi.org/10.5281/zenodo.19051441"><img src="https://img.shields.io/badge/DOI-10.5281/zenodo.19051441-blue" alt="DOI"></a>
</p>

## Features

- Full evaluation pipeline for Text-to-SPARQL systems from JSONL inputs to exportable JSON results.
- Rich metric coverage for answer-set quality, text similarity, structural similarity, ranking, distance, and execution validity.
- Two execution backend families:
    - Local RDF graphs with RDFLib.
    - Remote SPARQL endpoints (QLever, Corese, Fuseki, GraphDB, Virtuoso, Blazegraph, etc.).
- Simple Python API for research workflows and reproducible experiment scripts.
- CLI to run evaluations and launch dashboards.
- Static dashboard export support for sharing reports without running a server.

## Prerequisites
- [Python](https://www.python.org/) 3.12 or later.
- [uv](https://docs.astral.sh/uv/) (recommended for local development) or pip.
- A SPARQL endpoint only if you use execution metrics with a remote KG (for example QLever/Corese).
- [Ollama](http://ollama.com/) only if you enable LLM-based metrics.
- QCan jar only if you use qcan-related metrics. The repository includes it under [third_party_lib](https://github.com/Wimmics/t2s-metrics/tree/main/third_party_lib).

## Installation

### PyPI
For users who only want to run the library and CLI:

```bash
pip install t2s-metrics
```

After installation, the CLI entry point is available as:

```bash
cli --help
```

### For development (editable install):

1. Clone the repository:
```bash
git clone https://github.com/Wimmics/t2s-metrics.git
```

2. Navigate to the project directory:
```bash
cd t2s-metrics
```

3. Install dependencies

#### Using `uv`:
```bash
uv sync

# With dev dependencies (pytest, ruff, twine)
uv sync --all-extras
```

#### Using `pip`:
```bash
pip install -e .

# With dev dependencies (pytest, ruff, twine)
pip install -e ".[dev]"
```

## Usage

This section focuses on practical usage for both PyPI users and repository users.

### 1. Prepare your evaluation data

Input files must be JSON Lines (`.jsonl`) with one object per line.

Required keys:

- `id`: unique query/case identifier.
- `golden`: reference SPARQL query.
- `generated`: system-generated SPARQL query.
- `order_matters`: whether result ordering must be preserved.

Example (from [datasets/ck25/eval/AIFB.jsonl](https://github.com/Wimmics/t2s-metrics/blob/main/datasets/ck25/eval/AIFB.jsonl)):

```json
{"id": "ck25:1-en", "golden": "PREFIX pv: <http://ld.company.org/prod-vocab/>\nSELECT DISTINCT ?result\nWHERE\n{\n  <http://ld.company.org/prod-instances/empl-Karen.Brant%40company.org> pv:memberOf ?result .\n  ?result a pv:Department .\n}\n", "generated": "SELECT ?department WHERE { ?person :name \"Ms. Brant\"; :worksIn ?department. }", "order_matters": false}
```

### 2. Choose your execution backend

You must provide one execution backend when running execution-aware metrics:

- Local graph file with `--execution_backend_graph_path`.
- SPARQL endpoint URL with `--execution_backend_endpoint_url`.

Python examples:

```python
from t2smetrics.execution.rdflib_backend import RDFLibBackend
from t2smetrics.execution.sparql_endpoint_backend import SparqlEndpointBackend

# Local file backend
local_backend = RDFLibBackend("./datasets/example/kg/example.ttl")

# Remote endpoint backend
endpoint_backend = SparqlEndpointBackend("http://localhost:8886/")
```

### 3. Run from Python (based on run_example.py)

The minimal complete workflow from `t2smetrics/run_example.py`:

```python
from t2smetrics import run_experiments
from t2smetrics.metrics import (
    AnswerSetPrecision,
    AnswerSetRecall,
    AnswerSetF1,
    Bleu,
    CodeBLEU,
    QueryExecution,
    QueryExactMatch,
)

run_experiments.run(
    dataset="example",
    jsonl_evals=["./datasets/example/eval/example.jsonl"],
    metrics_list=[
        AnswerSetPrecision(),
        AnswerSetRecall(),
        AnswerSetF1(),
        Bleu(),
        CodeBLEU(),
        QueryExecution(),
        QueryExactMatch(),
    ],
    execution_backend_graph_path="./datasets/example/kg/example.ttl",
    verbose=True,
)
```

### 4. Run from Python on ck25 (based on run_text2sparql.py)

`t2smetrics/run_text2sparql.py` demonstrates a multi-system run on [ck25 dataset](https://github.com/AKSW/text2sparql.aksw.org/tree/2025) with an endpoint backend and parallel execution.

```bash
uv run ./t2smetrics/run_text2sparql.py
```

This generates timestamped JSON results under:

```text
datasets/ck25/results/ck25-YYYYMMDD-HHMMSS.json
```

### 5. Run from CLI (recommended for daily use)

Show command help:

```bash
cli --help
cli run --help
```

Example command (as requested):

```bash
cli run -d ck25 -j ./datasets/ck25/eval/ -m 'hit@1' 'answerset_f1' 'answerset_precision' 'answerset_recall' 'bleu' 'codebleu' 'cosine_sim' 'euclidean' 'f1_qald' 'f1_spinach' 'jaccard' 'levenshtein' 'meteor' 'mrr' 'ndcg' 'p@1' 'precision_qald' 'query_exact_match' 'recall_qald' 'rouge_4' 'sp-bleu' 'sp-f1' 'token_f1' 'token_precision' 'token_recall' 'uri_hallucination' 'query_execution' -ee http://localhost:8886/
```

Common useful flags:

- `-s/--systems_name` for explicit system names.
- `-p/--parallel` for multiprocessing.
- `-eq/--export_per_query` to include per-query values in output JSON.
- `-ep/--export_path` to control output location.
- `-eg/--execution_backend_graph_path` to run on local RDF files instead of endpoint mode.

### 6. Launch the dashboard

Auto-discover results under `datasets/*/results/*.json`:

```bash
cli dashboard
```

Load explicit result files:

```bash
cli dashboard -f \
  datasets/ck25/results/ck25-20260306-133227.json \
  datasets/db25/results/db25-20260306-132100.json
```

Generate a static dashboard snapshot:

```bash
cli dashboard --static --output static_dashboard_snapshot
```

Then open:

```text
http://127.0.0.1:8050
```

## Development

### Build

```bash
uv build
```

### Tests

Run the test suite with:

```bash
uv run pytest
```

## Release updates

For full details by version, see [CHANGELOG.md](./CHANGELOG.md).


## License

### t2s-metrics

t2s-metrics is provided under the terms of the [GNU Affero General Public License 3.0](./LICENSES/AGPL-3.0.txt) (AGPL-3.0).


### Redistribution of third-party software and data

This repository provides several third-party contributions redistributed with their original licenses.

#### CK25 Dataset

t2s-metrics reuses the [CK25 Corporate Knowledge Reference Dataset for Benchmarking Text-2-SPARQL QA Approaches](https://github.com/eccenca/ck25-dataset/) that we modified to account for file format requirements (jsonl format).

The modified version is redistributed in directory [dataset/ck25](dataset/ck25) under the terms of the [Creative Commons Attribution 4.0 International license](LICENSES/CC-BY-4.0.txt) (CC-BY-4.0).

#### QCan library

t2s-metrics reuses the [QCan software for canonicalising SPARQL queries](https://github.com/RittoShadow/QCan).

QCan is written in Java. In this repository, we distribute the compiled jar of QCan v1.1, [third_party_lib/qcan-1.1-jar-with-dependencies.jar](third_party_lib/qcan-1.1-jar-with-dependencies.jar), under the terms of the [Apache 2.0 license](LICENSES/Apache-2.0.txt).