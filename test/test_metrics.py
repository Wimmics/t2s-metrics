import pytest
from helpers import (
    DATA_DIR,
    check_available_file_cases,
    load_expectations,
    run_single_case,
    str_to_metric,
)

from t2smetrics.core.result import EvaluationResult

AVAILABLE_FILE_CASES = check_available_file_cases()


def get_cases():
    cases = []
    for file_case_id in AVAILABLE_FILE_CASES:
        expectations = load_expectations(
            DATA_DIR / "expectations" / f"{file_case_id}.yaml"
        )
        for case_id, metric_scores in expectations.items():
            for metric_name in metric_scores:
                cases.append(
                    (file_case_id, case_id, metric_name, metric_scores[metric_name])
                )
    return cases


@pytest.mark.parametrize(
    "file_case_id, case_id, metric_name, expected_score", get_cases()
)
def test_metrics(file_case_id, case_id, metric_name, expected_score):
    metric = str_to_metric(metric_name)
    result: EvaluationResult = run_single_case(
        file_cases_id=file_case_id,
        case_id=case_id,
        metrics={metric},
    )

    assert result.score == pytest.approx(expected_score, abs=1e-3)
