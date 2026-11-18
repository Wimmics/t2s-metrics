import json

import pytest

from t2smetrics import dashboard_plotly as dashboard
from t2smetrics import dashboard_plotly_static as static_dashboard


def test_plotly_dashboard_load_and_metric_options(tmp_path):
    path = tmp_path / "results.json"
    path.write_text(
        json.dumps(
            [
                {"system_name": "a", "metrics": {"bleu": 0.5}},
                {"system_name": "b", "metrics": {"bleu": 0.8, "mrr": 1}},
                {"system_name": "empty", "metrics": {}},
            ]
        )
    )
    loaded = dashboard.load_data(str(path))
    assert loaded[0]["systems"] == ["a", "b"]
    assert loaded[0]["metrics"] == ["bleu", "mrr"]
    assert loaded[-1] is False
    assert dashboard.load_data(None)[3] == "No file selected"
    invalid = tmp_path / "invalid.json"
    invalid.write_text("[]")
    assert dashboard.load_data(str(invalid))[3] == "No valid data in file"
    assert dashboard.stored_data_to_df(loaded[0]).shape == (2, 3)
    assert dashboard.stored_data_to_df({}).empty
    assert dashboard.update_heatmap_metrics(None) == []
    assert dashboard.update_heatmap_metrics(["bleu"]) == [{"label": "bleu", "value": "bleu"}]
    assert dashboard.update_parallel_coords_metrics([]) == []
    assert dashboard.update_scatter_metrics(["mrr"])[0]["value"] == "mrr"


def test_plotly_chart_callbacks_handle_empty_and_selected_data():
    empty = dashboard.update_radar_and_bar({}, [], None)
    assert len(empty) == 2
    stored = {
        "systems": ["a", "b"],
        "metrics": ["bleu", "mrr"],
        "data_matrix": [[0.5, 0.2], [0.8, 1.0]],
    }
    figures = dashboard.update_radar_and_bar(
        stored, ["a", "b"], "Standard NLP Metrics (String Based)"
    )
    assert len(figures) == 2
    assert dashboard.update_heatmap(stored, ["bleu"], ["a", "b"]) is not None
    assert dashboard.update_parallel(stored, ["bleu"], ["a", "b"]) is not None
    assert dashboard.update_scatter_matrix(stored, ["bleu", "mrr"], ["a", "b"]) is not None


def test_static_dashboard_validates_loads_and_builds(tmp_path):
    with pytest.raises(FileNotFoundError):
        static_dashboard._validate_and_resolve_files([str(tmp_path / "missing.json")])
    txt = tmp_path / "file.txt"
    txt.write_text("")
    with pytest.raises(ValueError):
        static_dashboard._validate_and_resolve_files([str(txt)])

    path = tmp_path / "results.json"
    path.write_text(json.dumps([{"system_name": "a", "metrics": {"bleu": 0.5}}, {}]))
    resolved = static_dashboard._validate_and_resolve_files([str(path)])
    payload = static_dashboard._load_dataset_payload(resolved)
    assert payload["datasets"][str(resolved[0])]["systems"] == ["a"]
    assert "Text2SPARQL Metrics Evaluation Dashboard" in static_dashboard._build_html(payload)
    assert "function" in static_dashboard._build_js()
