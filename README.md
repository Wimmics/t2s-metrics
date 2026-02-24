# T2S-Metrics

A small evaluation toolkit for text-to-SPARQL systems. It runs a configurable set
of metrics over JSONL datasets and can execute queries against local RDF files or
SPARQL endpoints.

## Features

- Metrics for query exact match, token overlap, answer-set quality, BLEU/ROUGE,
  CodeBLEU, and more.
- Execution backends for local RDF (RDFLib) and remote SPARQL endpoints.
- Pluggable LLM-based judging via an Ollama backend.
- CLI and Python API for quick experiments.

## Installation

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
uv pip install -e .
```

## Usage

### CLI

```bash
python -m t2smetrics.cli --dataset example_dataset.jsonl
```

### Python (minimal example)

```python
from t2smetrics.core.dataset import JsonlDataset
from t2smetrics.core.experiment import Experiment
from t2smetrics.measures.token import TokenPrecision, TokenRecall, TokenF1
from t2smetrics.measures.exact import QueryExactMatch

dataset = JsonlDataset("./example_dataset.jsonl")
measures = [TokenPrecision(), TokenRecall(), TokenF1(), QueryExactMatch()]

exp = Experiment(dataset, measures)
results, summary = exp.run()

print("=== SUMMARY ===")
for k, v in summary.items():
	print(f"{k}: {v:.4f}")
```

### Python (full example with execution backends)

```python
from t2smetrics.core.experiment import Experiment
from t2smetrics.core.dataset import JsonlDataset
from t2smetrics.execution.rdflib_backend import RDFLibBackend

from t2smetrics.llm.ollama_backend import OllamaBackend
from t2smetrics.measures.answer_set.f1 import AnswerSetF1
from t2smetrics.measures.answer_set.precision import AnswerSetPrecision
from t2smetrics.measures.answer_set.recall import AnswerSetRecall
from t2smetrics.measures.exact import QueryExactMatch
from t2smetrics.measures.codebleu.codebleu import CodeBLEU
from t2smetrics.measures.text_metrics import Bleu, RougeN, Meteor
from t2smetrics.measures.query_execution import QueryExecution
from t2smetrics.measures.token import TokenRecall, TokenPrecision, TokenF1

dataset = JsonlDataset("./example_dataset.jsonl")
execution_backend = RDFLibBackend("example.ttl")
llm_backend = OllamaBackend()

measures = [
	AnswerSetPrecision(),
	AnswerSetRecall(),
	AnswerSetF1(),
	Bleu(),
	CodeBLEU(),
	Meteor(),
	QueryExecution(),
	QueryExactMatch(),
	RougeN(4),
	TokenF1(),
	TokenPrecision(),
	TokenRecall(),
]

experiment = Experiment(
	dataset=dataset,
	measures=measures,
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

### Example scripts

```bash
python -m t2smetrics.run_example
python -m t2smetrics.run_text2sparql
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

See the [LICENSE file](./LICENSE).

## Cite this work

...


<details>
<summary>See BibTex</summary>
@inproceedings{,
...
}
</details>