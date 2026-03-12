# T2S-Metrics

A small evaluation toolkit for text-to-SPARQL systems. It runs a configurable set
of metrics over JSONL datasets and can execute queries against local RDF files or
SPARQL endpoints.

## Features

- Metrics for query exact match, token overlap, answer-set quality, BLEU/ROUGE,
  CodeBLEU, and more.
- Execution backends for local RDF (RDFLib) and remote SPARQL endpoints.
- Pluggable LLM-based judging via an Ollama backend.
- Python API for quick experiments.

## Installation

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
uv pip install -e .
```

## Usage

### Expected JSONL format

Input evaluation files must be JSON Lines (`.jsonl`) with **one object per line**.
Each object must include:

- `id` (string): unique query/case identifier
- `golden` (string): reference SPARQL query
- `generated` (string): system-generated SPARQL query
- `order_matters` (boolean): whether answer order must be preserved

This is exactly what `JsonlEval` expects in `t2smetrics/core/eval.py`.

Example (from `datasets/ck25/eval/AIFB.jsonl`):

```json
{"id": "ck25:1-en", "golden": "PREFIX pv: <http://ld.company.org/prod-vocab/>\nSELECT DISTINCT ?result\nWHERE\n{\n  <http://ld.company.org/prod-instances/empl-Karen.Brant%40company.org> pv:memberOf ?result .\n  ?result a pv:Department .\n}\n", "generated": "SELECT ?department WHERE { ?person :name \"Ms. Brant\"; :worksIn ?department. }", "order_matters": false}
```

### Execution backends

The library supports two execution backend families:

1. **Local RDF file execution** with `RDFLibBackend`
2. **Remote SPARQL endpoint execution** with `SparqlEndpointBackend`

`SparqlEndpointBackend` is generic SPARQL 1.1 and works with endpoints such as
**QLever** and **Corese** (and also GraphDB, Fuseki, Virtuoso, Blazegraph, etc.).

```python
from t2smetrics.execution.rdflib_backend import RDFLibBackend
from t2smetrics.execution.sparql_endpoint_backend import SparqlEndpointBackend

# Option 1: local KG file
local_backend = RDFLibBackend("./datasets/example/kg/example.ttl")

# Option 2: remote endpoint (e.g., QLever/Corese)
endpoint_backend = SparqlEndpointBackend("http://localhost:8886/")
```

### LLM backend (local Ollama + extensible)

For LLM-based metrics (for example `LLMJudge`), the library currently provides
`OllamaBackend` for **local** inference.

```python
from t2smetrics.llm.ollama_backend import OllamaBackend

llm_backend = OllamaBackend(model="gemma3:4b")
```

The LLM layer is extensible via `LLMBackend` (`t2smetrics/llm/base.py`).
To plug another provider, implement `judge(prompt: str, timeout: int = 30) -> dict`
and return a dictionary with a numeric `score` (recommended in `[0, 1]`).

```python
from t2smetrics.llm.base import LLMBackend


class MyLLMBackend(LLMBackend):
    def judge(self, prompt: str, timeout: int = 30) -> dict:
        # Call your provider/client here
        return {"score": 0.85, "raw": "optional provider response"}
```

Then pass your backend to `Experiment(..., llm_backend=...)`.

### Python (minimal example)

```python
from t2smetrics.core.experiment import Experiment
from t2smetrics.core.eval import JsonlEval
from t2smetrics.metrics.text_metrics import Bleu
from t2smetrics.metrics.token import TokenF1


jsonl_eval = JsonlEval("./datasets/example/eval/example.jsonl")
metrics = [Bleu(), TokenF1()]
experiment = Experiment(jsonl_eval, metrics)
_, summary = experiment.run()

print("\n=== SUMMARY ===")
for k, v in summary.items():
    print(f"{k}: {v:.4f}")
```

### Python (full example with execution backends)

```python
from t2smetrics.core.experiment import Experiment
from t2smetrics.core.eval import JsonlEval
from t2smetrics.execution.rdflib_backend import RDFLibBackend

from t2smetrics.llm.ollama_backend import OllamaBackend
from t2smetrics.metrics.answer_set.f1 import AnswerSetF1
from t2smetrics.metrics.answer_set.precision import AnswerSetPrecision
from t2smetrics.metrics.answer_set.precision_qald import PrecisionQALD
from t2smetrics.metrics.answer_set.recall import AnswerSetRecall
from t2smetrics.metrics.answer_set.recall_qald import RecallQALD
from t2smetrics.metrics.exact import QueryExactMatch
from t2smetrics.metrics.codebleu.codebleu import CodeBLEU
from t2smetrics.metrics.answer_set.f1_qald import F1QALD
from t2smetrics.metrics.answer_set.f1_spinach import F1Spinach
from t2smetrics.metrics.answer_set.mrr import MRR
from t2smetrics.metrics.answer_set.hit_at_k import HitAtK
from t2smetrics.metrics.answer_set.ndcg import NDCG
from t2smetrics.metrics.answer_set.p_at_k import PrecisionAtK
from t2smetrics.metrics.distance import (
    LevenshteinDistance,
    JaccardSimilarity,
    CosineSimilarity,
    EuclideanDistance,
)
from t2smetrics.metrics.llm_judge import LLMJudge
from t2smetrics.metrics.text_metrics import Bleu, RougeN, Meteor, SPBleu
from t2smetrics.metrics.uri.uri_hallucination import URIHallucination
from t2smetrics.metrics.query_execution import QueryExecution
from t2smetrics.metrics.token import SPF1, TokenRecall, TokenPrecision, TokenF1


jsonl_eval = JsonlEval("./datasets/example/eval/example.jsonl")

execution_backend = RDFLibBackend("./datasets/example/kg/example.ttl")

llm_backend = OllamaBackend()

metrics = [
    AnswerSetPrecision(),
    AnswerSetRecall(),
    AnswerSetF1(),
    Bleu(),
    SPBleu(),
    CodeBLEU(),
    CosineSimilarity(),
    EuclideanDistance(),
    F1QALD(),
    PrecisionQALD(),
    RecallQALD(),
    F1Spinach(),
    HitAtK(k=5),
    JaccardSimilarity(),
    LLMJudge(),
    LevenshteinDistance(),
    MRR(),
    Meteor(),
    NDCG(),
    PrecisionAtK(k=1),
    QueryExecution(),
    QueryExactMatch(),
    RougeN(1),
    RougeN(2),
    RougeN(3),
    RougeN(4),
    TokenF1(),
    SPF1(),
    TokenPrecision(),
    TokenRecall(),
    URIHallucination(),
]

experiment = Experiment(
    jsonl_eval=jsonl_eval,
    metrics=metrics,
    execution_backend=execution_backend,
    llm_backend=llm_backend,
    verbose=True,
)

results, summary = experiment.run()

print("=== PER QUERY RESULTS ===")
for r in results:
    print(r)

print("\n=== SUMMARY ===")
for k, v in summary.items():
    print(f"{k}: {v:.4f}")
```

### Full workflow example (dataset + endpoint + export)

For a complete run over multiple systems and export of aggregated metrics to JSON,
see `t2smetrics/run_text2sparql.py`.

Typical workflow:

1. Choose a dataset folder (for example `datasets/ck25`).
2. Put input files under `datasets/<dataset>/eval/*.jsonl`.
3. Start your SPARQL endpoint (for example QLever/Corese).
4. Set endpoint URL in the script (example: `http://localhost:8886/`).
5. Run:

```bash
python -m t2smetrics.run_text2sparql
```

The script writes timestamped summary files under:

```text
datasets/<dataset>/results/<dataset>-YYYYMMDD-HHMMSS.json
```

These result files are then directly consumable by the dashboard.

### Dashboard

The dashboard reads JSON result files (generated in `datasets/*/results/*.json`)
and serves an interactive UI (Radar, Bar, Correlation Heatmap, Parallel Coordinates,
Scatter Matrix).

Launch with auto-discovery:

```bash
python -m t2smetrics.cli dashboard
```

Launch with explicit files:

```bash
python -m t2smetrics.cli dashboard \
    datasets/ck25/results/ck25-20260306-133227.json \
    datasets/db25/results/db25-20260306-132100.json
```

Then open:

```text
http://127.0.0.1:8050
```


## Development

### Build

```bash
python setup.py sdist bdist_wheel
```

### Tests

There are no automated tests yet. If you add tests, run them with:

```bash
python -m pytest
```

# License

## t2s-metrics

t2s-metrics is provided under the terms of the [GNU Affero General Public License 3.0](./LICENSES/AGPL-3.0.txt) (AGPL-3.0).


## Redistribution of third-party software and data

This repository provides several third-party contributions redistributed with their original licenses.

### CK25 Dataset

t2s-metrics reuses the [CK25 Corporate Knowledge Reference Dataset for Benchmarking Text-2-SPARQL QA Approaches](https://github.com/eccenca/ck25-dataset/) that we modified to account for file format requirements (jsonl format).

The modified version is redistributed in directory [dataset/ck25](dataset/ck25) under the terms of the [Creative Commons Attribution 4.0 International license](LICENSES/CC-BY-4.0.txt) (CC-BY-4.0).

### QCan library

t2s-metrics reuses the [QCan software for canonicalising SPARQL queries](https://github.com/RittoShadow/QCan).

QCan is written in Java. In this repository, we distribute the compiled jar of QCan v1.1, [third_party_lib/qcan-1.1-jar-with-dependencies.jar](third_party_lib/qcan-1.1-jar-with-dependencies.jar), under the terms of the [Apache 2.0 license](LICENSES/Apache-2.0.txt).