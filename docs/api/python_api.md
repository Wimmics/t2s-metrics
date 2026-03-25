# Python API Reference

## High-level orchestration

Primary entrypoint:

- `t2smetrics.run_experiments.run(...)`

Core parameters:

- `jsonl_evals`: list of input JSONL paths or folders
- `metrics_list`: metric names or metric instances
- `dataset`: dataset label for exports
- `execution_backend_graph_path` or `execution_backend_endpoint_url`
- `parallel`: run multiple systems in parallel
- `per_query`: include per-query values in result export

## Experiment internals

- `JsonlEval`: iterates `QueryCase` rows from JSONL
- `Experiment`: wraps context, engine, and aggregation
- `EvaluationEngine`: executes metrics with requirement checks

## Metric registry

- `t2smetrics.metrics.metrics_utils.get_metric_mapping()` returns registered metrics.
- `t2smetrics.metrics.metrics_utils.str_to_metric(name)` resolves a metric name to an instance.
