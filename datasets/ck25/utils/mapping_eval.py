"""This is a mapping evaluation utility for the CK25 dataset results. The official results can be found at:
https://github.com/AKSW/text2sparql.aksw.org/tree/2025/docs/results
"""

import json

import yaml

datasets = ["ck25", "db25"]
qa_systems = [
    "AIFB",
    "DBPEDIA-CG",
    "DBPEDIA-CL",
    "DBPEDIA-SC",
    "FRANZ",
    "IIS-L",
    "IIS-Q",
    "INFAI",
    "LABIC",
    "LACODAM",
    "MIPT",
    "WSE",
]

languages = ["en", "es"]

for dataset in datasets:
    for qa_system in qa_systems:
        with open(
            f"docs/results/{qa_system}/{dataset}_answers.json"
        ) as f_gen_ck25:
            f_gen_data = json.load(f_gen_ck25)

        with open(f"docs/benchmark/questions_{dataset}.yaml") as f_gold_ck25:
            content = f_gold_ck25.read()
            f_gold_data = yaml.safe_load(content)

        collected_data = []
        for gold_item in f_gold_data["questions"]:
            for language in languages:
                try:
                    item = next(
                        item
                        for item in f_gen_data
                        if item["qname"] == f"{dataset}:{gold_item['id']}-{language}"
                    )
                    collected_data.append(
                        {
                            "id": f"{dataset}:{gold_item['id']}-{language}",
                            "golden": gold_item["query"]["sparql"],
                            "generated": item["query"],
                            "order_matters": (
                                bool("features" in gold_item and "RESULT_ORDER_MATTERS" in gold_item["features"])
                            ),
                        }
                    )
                except StopIteration:
                    pass

        # Save the collected data to a JSONL file. the exports directory should be created beforehand.
        with open(f"datasets/{dataset}/eval/{qa_system}.jsonl", "w") as f:
            for item in collected_data:
                f.write(json.dumps(item) + "\n")
