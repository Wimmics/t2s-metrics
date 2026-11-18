from unittest.mock import Mock

import pytest

from t2smetrics import cli


def test_cli_parsers_capture_run_filter_and_dashboard_options():
    parser = cli.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    cli.get_run_experiments_parser(subparsers)
    cli.get_filter_parser(subparsers)
    cli.get_dashboard_parser(subparsers)

    args = parser.parse_args(["run", "-j", "cases.jsonl", "-m", "bleu"])
    assert args.command == "run"
    assert args.metrics == ["bleu"]
    args = parser.parse_args(["dashboard", "-s", "-p", "9000"])
    assert args.static is True and args.port == 9000
    args = parser.parse_args(
        ["filter", "-d", "example", "-j", "x.jsonl", "-r", "f1[1]"]
    )
    assert args.rule == "f1[1]"


def test_cli_main_dispatches_commands(monkeypatch):
    run = Mock()
    monkeypatch.setattr("t2smetrics.run_experiments.run", run)
    monkeypatch.setattr(cli.sys, "argv", ["t2s", "run", "-j", "x.jsonl", "-m", "bleu"])
    cli.main()
    run.assert_called_once()

    dashboard = Mock()
    monkeypatch.setattr("t2smetrics.dashboard_plotly.run", dashboard)
    monkeypatch.setattr(cli.sys, "argv", ["t2s", "dashboard"])
    cli.main()
    dashboard.assert_called_once()

    filter_run = Mock()
    monkeypatch.setattr("t2smetrics.core.filterer.run_filter", filter_run)
    monkeypatch.setattr(
        cli.sys, "argv", ["t2s", "filter", "-d", "d", "-j", "x", "-r", "f1[1]"]
    )
    cli.main()
    filter_run.assert_called_once()

    monkeypatch.setattr(cli.sys, "argv", ["t2s"])
    with pytest.raises(SystemExit):
        cli.main()
