import re

VAR_PATTERN = re.compile(r"\?[a-zA-Z_]\w*")


def extract_vars(query: str) -> set[str]:
    return set(VAR_PATTERN.findall(query))


def dataflow_match(gold: str, pred: str) -> float:
    gold_vars = extract_vars(gold)
    pred_vars = extract_vars(pred)

    if not gold_vars:
        return 1.0

    overlap = gold_vars & pred_vars
    return len(overlap) / len(gold_vars)
