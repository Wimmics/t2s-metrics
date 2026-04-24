from collections import Counter

import numpy as np
from scipy.optimize import linear_sum_assignment

from t2smetrics.core.result import EvaluationResult
from t2smetrics.metrics.answer_set.base import AnswerSetMeasure


class ExactMatchSpinach(AnswerSetMeasure):
    name = "exact_match_spinach"

    def compute(self, case, context):
        gold, pred = self._get_answer_json_whitout_normalisation(case, context)

        if type(pred) is bool or type(gold) is bool:
            return EvaluationResult(case.id, self.name, float(pred == gold))

        score = float(self._exact_match_with_additional_columns(pred, gold))
        return EvaluationResult(case.id, self.name, score)

    def _exact_match_with_additional_columns(self, predicted_results, gold_results):
        if predicted_results is None or gold_results is None:
            return False

        if len(predicted_results) != len(gold_results):
            return False

        if len(gold_results) == 0:
            return True

        # Build a binary compatibility matrix for one-to-one row matching.
        compatibility = np.zeros((len(predicted_results), len(gold_results)))

        for i, predicted in enumerate(predicted_results):
            for j, gold in enumerate(gold_results):
                compatibility[i, j] = (
                    1.0 if self._row_covers_gold(predicted, gold) else 0.0
                )

        row_ind, col_ind = linear_sum_assignment(compatibility, maximize=True)

        return compatibility[row_ind, col_ind].sum() == len(gold_results)

    def _row_covers_gold(self, predicted, gold):
        gold_values = [
            tuple(sorted(gold_value.items())) for gold_value in gold.values()
        ]
        predicted_values = [
            tuple(sorted(predicted_value.items()))
            for predicted_value in predicted.values()
        ]

        gold_counter = Counter(gold_values)
        predicted_counter = Counter(predicted_values)

        return all(
            predicted_counter[value] >= count for value, count in gold_counter.items()
        )
