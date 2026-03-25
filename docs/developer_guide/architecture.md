# Architecture

`t2s-metrics` is organized as a modular evaluation pipeline.

## Main flow

1. `JsonlEval` iterates query cases from JSONL input.
2. `Experiment` creates context and evaluation engine.
3. `EvaluationEngine` runs metrics per case.
4. `MeanAggregator` computes summary values.
5. Export utilities write JSON result files.

## Core packages

- `t2smetrics/core`: context, engine, experiment orchestration, export
- `t2smetrics/metrics`: metric definitions and registry
- `t2smetrics/execution`: local and endpoint query execution backends
- `t2smetrics/llm`: optional LLM backend for judge-style metrics
- `t2smetrics/representation`: SPARQL preprocessing/tokenization utilities

## Runtime constraints

- Metrics can declare execution or LLM requirements.
- The engine enforces requirements before computing each metric.
- `ndcg` is skipped when `order_matters` is false in the input case.
