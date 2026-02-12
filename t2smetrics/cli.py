import argparse

from t2smetrics.core.dataset import JsonlDataset
from t2smetrics.core.experiment import Experiment
from t2smetrics.measures.token import TokenPrecision, TokenRecall, TokenF1
from t2smetrics.measures.exact import QueryExactMatch


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    args = parser.parse_args()

    dataset = JsonlDataset(args.dataset)

    measures = [
        TokenPrecision(),
        TokenRecall(),
        TokenF1(),
        QueryExactMatch(),
    ]

    exp = Experiment(dataset, measures)
    results, summary = exp.run()

    print("=== SUMMARY ===")
    for k, v in summary.items():
        print(f"{k}: {v:.4f}")


if __name__ == "__main__":
    main()
