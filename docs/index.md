# t2s-metrics Documentation

A lightweight evaluation toolkit for Text-to-SPARQL systems.

```{toctree}
:maxdepth: 2
:caption: Contents

getting_started/index
user_guides/index
developer_guide/index
api/index
```

## What is t2s-metrics?

`t2s-metrics` provides a configurable evaluation pipeline for Text-to-SPARQL systems:

- Load query pairs from JSONL files.
- Run a metric suite (exact-match, answer-set, token/text, execution-aware, ranking, and distance metrics).
- Export reproducible JSON results.
- Explore outcomes in an interactive dashboard or static dashboard snapshot.

## Quick Links

- Installation and local setup: [Getting Started](getting_started/index.md)
- End-to-end execution flow: [Basic Workflow](user_guides/basic_workflow.md)
- Parallel runs, custom exports, and backend choices: [Advanced Usage](user_guides/advanced_usage.md)
- How internals fit together: [Architecture](developer_guide/architecture.md)
