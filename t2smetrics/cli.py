import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="T2S Metrics CLI",
    )
    subparsers = parser.add_subparsers(dest="command")

    # dashboard subcommand
    dashboard_parser = subparsers.add_parser(
        "dashboard",
        help="Launch the evaluation dashboard",
    )
    dashboard_parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="JSON result file(s) to load. If omitted, auto-discovers datasets/*/results/*.json",
    )

    args = parser.parse_args()

    if args.command == "dashboard":
        from t2smetrics import dashboard_plotly
        available_files = args.files if args.files else None
        dashboard_plotly.run(available_files=available_files)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
