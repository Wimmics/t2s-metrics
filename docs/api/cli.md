# CLI Reference

The project exposes a `t2s` command with three subcommands. Run `t2s --help`
or a subcommand's `--help` option for the generated list of registered metrics
and complete argument descriptions.

## `t2s run`

Runs evaluations and exports JSON results.

Key arguments:

- `-d`, `--dataset`: dataset name label
- `-j`, `--jsonl_evals`: one or more JSONL files or directories
- `-m`, `--metrics`: metric names or `__all__`
- `--eg`, `--execution_backend_graph_path`: local graph file
- `--ee`, `--execution_backend_endpoint_url`: SPARQL endpoint URL
- `--lo`, `--llm_backend_ollama_model`: Ollama model for LLM metrics
- `-p`, `--parallel`: multiprocessing across systems
- `--eq`, `--export_per_query`: include per-query values in export
- `--ep`, `--export_path`: custom output path
- `--sl`, `--safe_limit`: add a `LIMIT` to evaluated queries
- `--pp`, `--add_popular_prefixes`: add prefixes from prefix.cc
- `--cp`, `--add_custom_prefixes`: add a JSON prefix mapping

## `t2s filter`

Evaluates the metrics referenced by a boolean rule and exports matching cases as
WADM Turtle annotations.

Key arguments:

- `-d`, `--dataset`: dataset name label
- `-j`, `--jsonl_evals`: one or more JSONL files or directories
- `-r`, `--rule`: metric comparisons combined with `&&` and `||`; use
	`basicRule` for the built-in rule
- `-c`, `--convert label-studio`: additionally export Label Studio JSON and a
	template XML file
- `-ep`, `--export_path`: custom output file or directory
- `--sl`, `--safe_limit`: add a `LIMIT` to evaluated queries
- `--pp`, `--add_popular_prefixes`: add prefixes from prefix.cc
- `--cp`, `--add_custom_prefixes`: add a JSON prefix mapping

Rules use forms such as `answerset_f1[0.5,1]` and support inclusive or exclusive
range boundaries with `[` and `]`.

## `t2s dashboard`

Starts dashboard UI or builds a static snapshot.

Key arguments:

- `-f`, `--files`: explicit result files
- `-s`, `--static`: generate static output
- `-o`, `--output`: static output directory
- `-p`, `--port`: dashboard port (default `8050`)
