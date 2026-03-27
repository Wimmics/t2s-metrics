# CLI Reference

The project exposes a `t2s` command with two main subcommands.

## `t2s run`

Runs evaluations and exports JSON results.

Key arguments:

- `-d`, `--dataset`: dataset name label
- `-j`, `--jsonl_evals`: one or more JSONL files or directories
- `-m`, `--metrics`: metric names or `__all__`
- `-eg`, `--execution_backend_graph_path`: local graph file
- `-ee`, `--execution_backend_endpoint_url`: SPARQL endpoint URL
- `-lo`, `--llm_backend_ollama_model`: Ollama model for LLM metrics
- `-p`, `--parallel`: multiprocessing across systems
- `-eq`, `--export_per_query`: include per-query values in export
- `-ep`, `--export_path`: custom output path

## `t2s dashboard`

Starts dashboard UI or builds a static snapshot.

Key arguments:

- `-f`, `--files`: explicit result files
- `-s`, `--static`: generate static output
- `-o`, `--output`: static output directory
- `-p`, `--port`: dashboard port (default `8050`)
