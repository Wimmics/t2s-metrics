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
- `safe_limit`: add a `LIMIT` to queries before execution
- `add_popular_prefixes`: add popular prefixes from prefix.cc
- `add_custom_prefixes`: provide a custom prefix-to-namespace mapping

`run_experiments.run(...)` requires either `execution_backend_graph_path` or
`execution_backend_endpoint_url`. It returns the completed `Experiment` objects;
set `export_results=False` when another workflow will consume them directly.

## Rule-based filtering

`t2smetrics.core.filterer.run_filter(...)` evaluates the metrics referenced by a
boolean rule and exports matching cases as WADM Turtle. Set `convert="label-studio"`
to also produce Label Studio JSON and a template XML file. The filter workflow
accepts the same execution, Ollama, parallelism, safe-limit, and prefix options
as the CLI command.

## Experiment internals

- `JsonlEval`: iterates `QueryCase` rows from JSONL
- `Experiment`: wraps context, engine, and aggregation
- `EvaluationEngine`: executes metrics with requirement checks

## Metric registry

- `t2smetrics.metrics.metrics_utils.get_metric_mapping()` returns registered metrics.
- `t2smetrics.metrics.metrics_utils.str_to_metric(name)` resolves a metric name to an instance.
