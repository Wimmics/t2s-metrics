# Advanced Usage Guide

## Metric selection strategies

Use `__all__` to compute all registered metrics:

```bash
t2s run -d ck25 -j ./datasets/ck25/eval/ -m __all__ -ee http://localhost:8886/
```

Or run focused subsets depending on your evaluation question:

- Structural fidelity: `query_exact_match`, `token_f1`, `codebleu`
- Result quality: `answerset_precision`, `answerset_recall`, `answerset_f1`
- Ranking behavior: `mrr`, `ndcg`, `hit@1`, `p@1`

## Parallel execution

Enable multiprocessing across systems/files:

```bash
t2s run -d ck25 -j ./datasets/ck25/eval/ -m query_execution answerset_f1 -ee http://localhost:8886/ -p
```

## Export controls

Useful flags:

- `-eq` to include per-query scores
- `-ep` to write output to a custom location
- `-s` to set explicit system names

Example:

```bash
t2s run \
  -d ck25 \
  -s AIFB DBPEDIA-CG \
  -j ./datasets/ck25/eval/AIFB.jsonl ./datasets/ck25/eval/DBPEDIA-CG.jsonl \
  -m query_execution answerset_f1 \
  -ee http://localhost:8886/ \
  -eq \
  -ep ./datasets/ck25/results/custom-run.json
```

## LLM-based metrics

If selected metrics require LLM support, configure the Ollama model:

```bash
t2s run -d ck25 -j ./datasets/ck25/eval/ -m llm_judge -ee http://localhost:8886/ -lo gemma3:4b
```
