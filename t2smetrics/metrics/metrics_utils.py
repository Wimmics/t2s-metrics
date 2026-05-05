from t2smetrics.metrics import (
    F1QALD,
    MRR,
    NDCG,
    SPF1,
    AnswerSetF1,
    AnswerSetPrecision,
    AnswerSetRecall,
    Bleu,
    CodeBLEU,
    CosineSimilarity,
    EuclideanDistance,
    ExactMatchSpinach,
    F1Spinach,
    HitAtK,
    JaccardSimilarity,
    LevenshteinDistance,
    Meteor,
    PrecisionAtK,
    PrecisionQALD,
    QueryExactMatch,
    QueryExecution,
    RecallQALD,
    RougeN,
    SPBleu,
    TokenF1,
    TokenPrecision,
    TokenRecall,
    URIHallucination,
)
from t2smetrics.metrics.base import Metric
from t2smetrics.metrics.llm_judge import LLMJudge


def get_metric_mapping() -> dict[str, Metric]:
    """Returns a mapping of metric names to their corresponding Metric instances."""
    metrics: list[Metric] = [
        AnswerSetPrecision(),
        AnswerSetRecall(),
        AnswerSetF1(),
        PrecisionQALD(),
        RecallQALD(),
        F1QALD(),
        F1Spinach(),
        ExactMatchSpinach(),
        HitAtK(k=1),
        MRR(),
        NDCG(),
        PrecisionAtK(k=1),
        QueryExactMatch(),
        CosineSimilarity(),
        EuclideanDistance(),
        JaccardSimilarity(),
        LevenshteinDistance(),
        URIHallucination(),
        Bleu(),
        SPBleu(),
        SPF1(),
        Meteor(),
        RougeN(n=4),
        TokenPrecision(),
        TokenRecall(),
        TokenF1(),
        CodeBLEU(),
        LLMJudge(),
        QueryExecution(),
    ]

    return {metric.name: metric for metric in metrics}


def str_to_metric(metric_name: str) -> Metric:

    mapping = get_metric_mapping()

    if metric_name not in mapping:
        raise ValueError(f"Unknown metric name: {metric_name}")

    return mapping[metric_name]
