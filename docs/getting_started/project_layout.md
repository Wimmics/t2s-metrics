# Project Layout

Key folders:

- `t2smetrics/`: core library code
- `datasets/`: evaluation inputs, KGs, and results
- `test/`: test suite
- `third_party_lib/`: optional external assets such as QCan jar

Important modules in `t2smetrics/`:

- `cli.py`: command-line entrypoint
- `run_experiments.py`: orchestration for single or parallel experiment runs
- `core/`: evaluation context, engine, experiment, and export logic
- `metrics/`: metric implementations and registry
- `execution/`: local RDFLib and remote endpoint backends
- `dashboard_plotly.py`: dashboard runtime for result exploration
