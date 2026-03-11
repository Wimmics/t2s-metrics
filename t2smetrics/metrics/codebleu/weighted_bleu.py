from collections import Counter
from t2smetrics.metrics.codebleu.sparql_keywords import SPARQL_KEYWORDS


def weighted_precision(ref_tokens, pred_tokens):
    ref = Counter(ref_tokens)
    pred = Counter(pred_tokens)

    score = 0.0
    total = 0.0

    for tok, cnt in pred.items():
        weight = SPARQL_KEYWORDS.get(tok, 1.0)
        matched = min(cnt, ref.get(tok, 0))
        score += weight * matched
        total += weight * cnt

    return score / total if total > 0 else 0.0
