import shutil
import subprocess
import sys
from argparse import ArgumentParser, _SubParsersAction
from pathlib import Path

from loguru import logger

from t2smetrics.metrics.metrics_utils import get_metric_mapping


def get_run_experiments_parser(
    subparsers: "_SubParsersAction[ArgumentParser]",
) -> ArgumentParser:
    """Adds the 'run' subcommand parser to the provided subparsers action.

    Args:
        subparsers: The subparsers action to which the 'run' parser will be added.

    Returns:
        The ArgumentParser instance for the 'run' subcommand.
    """
    run_experiments_parser = subparsers.add_parser(
        "run",
        help="Run evaluation experiments and save results to a JSON file",
    )
    run_experiments_parser.add_argument(
        "-d",
        "--dataset",
        type=str,
        default="unknown",
        help="Dataset to evaluate (e.g., 'ck25')",
    )
    run_experiments_parser.add_argument(
        "-s",
        "--systems_name",
        type=str,
        default=[],
        nargs="+",
        help="System name (e.g., 'AIFB')",
    )
    run_experiments_parser.add_argument(
        "-j",
        "--jsonl_evals",
        type=str,
        nargs="+",
        help="Path(s) to JSONL evaluation files (e.g., './datasets/ck25/eval/AIFB.jsonl') or directories containing JSONL files (e.g., './datasets/ck25/eval/')",
        required=True,
    )

    available_metrics = sorted(get_metric_mapping().keys())

    # Create a nicely formatted help text
    help_metrics = f"""Metrics to compute or "__all__" to compute all available metrics.
    
    Available metrics:
    {", ".join(available_metrics)}
    """
    run_experiments_parser.add_argument(
        "-m",
        "--metrics",
        metavar="METRIC",
        choices=available_metrics + ["__all__"],
        nargs="+",
        help=help_metrics,
        required=True,
    )
    run_experiments_parser.add_argument(
        "-eg",
        "--execution_backend_graph_path",
        type=str,
        help="Path to the execution backend graph (e.g., './datasets/ck25/kg/dataset.ttl')",
    )
    run_experiments_parser.add_argument(
        "-ee",
        "--execution_backend_endpoint_url",
        type=str,
        help="SPARQL endpoint URL for the execution backend (e.g., 'http://localhost:3030/dataset/sparql')",
    )
    run_experiments_parser.add_argument(
        "-lo",
        "--llm_backend_ollama_model",
        default="gemma3:4b",
        type=str,
        help="LLM model name for Ollama backend (e.g., 'gemma3:4b')",
    )
    run_experiments_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output during experiment execution (default: False)",
    )
    run_experiments_parser.add_argument(
        "-ncr",
        "--no_cache_results",
        action="store_false",
        help="Do not cache query execution results (default: cache results)",
    )
    run_experiments_parser.add_argument(
        "-ep",
        "--export_path",
        type=str,
        help="Path to save the experiment results JSON file (default: './datasets/{dataset}/results/')",
    )
    run_experiments_parser.add_argument(
        "-eq",
        "--export_per_query",
        action="store_true",
        help="Include per-query results in the exported JSON file (default: False)",
    )
    run_experiments_parser.add_argument(
        "-p",
        "--parallel",
        action="store_true",
        help="Run experiments in parallel using multiprocessing (default: False)",
    )

    return run_experiments_parser


def get_dashboard_parser(
    subparsers: "_SubParsersAction[ArgumentParser]",
) -> ArgumentParser:
    """Adds the 'dashboard' subcommand parser to the provided subparsers action.

    Args:
        subparsers: The subparsers action to which the 'dashboard' parser will be added.

    Returns:
        The ArgumentParser instance for the 'dashboard' subcommand.
    """
    dashboard_parser = subparsers.add_parser(
        "dashboard",
        help="Launch the evaluation dashboard",
    )
    dashboard_parser.add_argument(
        "-f",
        "--files",
        nargs="*",
        metavar="FILE",
        help="JSON result file(s) to load. If omitted, auto-discovers datasets/*/results/*.json",
    )
    dashboard_parser.add_argument(
        "-s",
        "--static",
        action="store_true",
        help="Generate a static snapshot of the dashboard and store it in the specified output directory.",
    )
    dashboard_parser.add_argument(
        "-o",
        "--output",
        default="static_dashboard_snapshot",
        help="Output directory for static dashboard snapshot (default: 'static_dashboard_snapshot')",
    )
    dashboard_parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8050,
        help="Port to run the dashboard on (default: 8050)",
    )

    return dashboard_parser


def docs_build_html():
    """Build HTML documentation with Sphinx."""
    docs_dir = Path(__file__).parent.parent / "docs"
    build_dir = docs_dir / "_build" / "html"

    # Ensure docs directory exists
    if not docs_dir.exists():
        logger.error("Error: docs directory not found")
        sys.exit(1)

    # Run sphinx-build
    cmd = ["sphinx-build", "-b", "html", str(docs_dir), str(build_dir)]
    logger.info(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def docs_clean():
    """Clean built documentation."""
    docs_dir = Path(__file__).parent.parent / "docs"
    build_dir = docs_dir / "_build"

    if build_dir.exists():
        shutil.rmtree(build_dir)
        logger.info(f"Removed {build_dir}")
    else:
        logger.warning("No build directory found")


def main():
    parser = ArgumentParser(
        description="T2S Metrics CLI",
    )
    subparsers = parser.add_subparsers(dest="command")

    get_run_experiments_parser(subparsers)

    get_dashboard_parser(subparsers)

    args = parser.parse_args()

    if args.command == "dashboard":
        from t2smetrics import dashboard_plotly

        available_files = args.files if args.files else None
        static_mode = args.static
        output_dir = args.output
        port = args.port
        dashboard_plotly.run(
            available_files=available_files,
            static_mode=static_mode,
            output_dir=output_dir,
            port=port,
        )

    elif args.command == "run":
        from t2smetrics import run_experiments

        run_experiments.run(
            dataset=args.dataset,
            systems_name=args.systems_name,
            jsonl_evals=args.jsonl_evals,
            metrics_list=args.metrics,
            verbose=args.verbose,
            cache_results=args.no_cache_results,
            export_path=args.export_path,
            per_query=args.export_per_query,
            execution_backend_graph_path=args.execution_backend_graph_path,
            execution_backend_endpoint_url=args.execution_backend_endpoint_url,
            llm_backend_ollama_model=args.llm_backend_ollama_model,
            parallel=args.parallel,
        )

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
