import argparse

from t2smetrics.core.eval import JsonlEval
from t2smetrics.core.experiment import Experiment
from t2smetrics.metrics.token import TokenPrecision, TokenRecall, TokenF1
from t2smetrics.metrics.exact import QueryExactMatch


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jsonl_eval", required=True)
    args = parser.parse_args()

    jsonl_eval = JsonlEval(args.jsonl_eval)

    metrics = [
        TokenPrecision(),
        TokenRecall(),
        TokenF1(),
        QueryExactMatch(),
    ]

    exp = Experiment(jsonl_eval=jsonl_eval, metrics=metrics)
    results, summary = exp.run()

    print("=== SUMMARY ===")
    for k, v in summary.items():
        print(f"{k}: {v:.4f}")


if __name__ == "__main__":
    main()
