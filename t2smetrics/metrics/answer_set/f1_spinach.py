import logging
from collections import Counter

import numpy as np
from scipy.optimize import linear_sum_assignment

from t2smetrics.core.result import EvaluationResult
from t2smetrics.metrics.answer_set.base import AnswerSetMeasure
from t2smetrics.metrics.answer_set.f1 import AnswerSetF1

logger = logging.getLogger(__name__)


# The official implementation at: https://github.com/stanford-oval/spinach/blob/8bb2d9cfa7f54b7b63ba5e6acd8264fdb7f8ecf9/eval.py#L108
class F1Spinach(AnswerSetMeasure):
    name = "f1_spinach"

    def compute(self, case, context):
        # gold, pred = self._get_answer_lists(case, context)
        gold, pred = self._get_answer_json_whitout_normalisation(case, context)

        if type(pred) is bool or type(gold) is bool:
            f1 = int(pred == gold)
            return EvaluationResult(case.id, self.name, f1)

        if len(pred) * len(gold) > 1000000:
            logger.warning(
                "The number of comparisons for F1Spinach is %d, which may lead to long computation time.",
                len(pred) * len(gold),
            )
            logger.warning(
                "Falling back to a simpler F1 computation without maximal matching."
            )
            return AnswerSetF1().compute(case, context)

        f1 = self.f1(pred, gold)
        return EvaluationResult(case.id, self.name, f1)

    def f1(self, predicted_results, gold_results, maximal_matching=True):
        """Calculates a row-major F1 score for each example.
        """
        if predicted_results is None:
            return 0

        if type(predicted_results) is bool or type(gold_results) is bool:
            return int(predicted_results == gold_results)

        if maximal_matching:
            # first compute a cost matrix between `predicted_results` and `gold_results`
            cost_matrix = np.empty((len(predicted_results), len(gold_results)))

            for i in range(len(predicted_results)):
                for j in range(len(gold_results)):
                    i_j_recall = self._compute_match_ratio(
                        predicted_results[i], gold_results[j]
                    )
                    cost_matrix[i, j] = i_j_recall

            row_ind, col_ind = linear_sum_assignment(cost_matrix, maximize=True)

            assigned_values = cost_matrix[row_ind, col_ind]

            # true positives are those that get matched (times their respective row-by-row recall)
            tp = assigned_values[assigned_values > 0].sum()

            # each matched row below 1 but above 0 will count as 1 - recall(i,j) to false negatives
            below_one_above_zero = assigned_values[
                (assigned_values < 1) & (assigned_values > 0)
            ]
            fp_or_fn = (1 - below_one_above_zero).sum()

            # each matched row PAIR with 0 match rate will count as 1 false negative and 1 false positive
            fp_or_fn += 2 * np.sum(assigned_values <= 0)

            # each individual unmatched row (due to cost matrix being rectangular) will
            # count as either 1 false negative or 1 false positive
            fp_or_fn += (len(predicted_results) - len(row_ind)) + (
                len(gold_results) - len(col_ind)
            )

            res = 0 if 2 * tp + fp_or_fn == 0 else 2 * tp / (2 * tp + fp_or_fn)

        else:
            # an older implmentation with greedy matching
            # SHOULD NO LONGER BE USED
            gold_result_mapping = [
                [gold_result, False]
                for gold_result in gold_results  # false denoting not matched yet
            ]

            tp = 0
            fp = 0
            fn = 0

            for predicted_result in predicted_results:
                candidate_index = None
                match_ratio = 0

                # go over gold results yet to be matched to find the one with most matches
                # greedily match that to this
                for index, gold_result in enumerate(gold_result_mapping):
                    if gold_result[1]:
                        continue

                    gold_result = gold_result[0]
                    this_match_ratio = self._compute_match_ratio(
                        predicted_result, gold_result
                    )
                    if this_match_ratio > match_ratio:
                        match_ratio = this_match_ratio
                        candidate_index = index

                if candidate_index is not None:
                    gold_result_mapping[candidate_index][1] = True

                if match_ratio == 0:
                    fp += 1
                else:
                    tp += match_ratio
                    fn += 1 - match_ratio

            fn += len(list(filter(lambda x: not x[1], gold_result_mapping)))

            res = 2 * tp / (2 * tp + fp + fn)

        assert res >= 0
        assert res <= 1

        return res

    def _compute_match_ratio(self, predicted, gold):
        """Example `predicted` or `gold`:
        {
            "item": {
            "type": "uri",
            "value": "http://www.wikidata.org/entity/Q98926"
            },
            "itemLabel": {
            "type": "literal",
            "value": "Lola Landau",
            "xml:lang": "en"
            }
        }
        """
        gold_values = [
            tuple(sorted(gold_value.items()))
            for gold_key, gold_value in gold.items()
            if not (gold_key.endswith("Label") or gold_key.endswith("Description"))
        ]
        useful_predicted_values = [
            tuple(sorted(predicted_value.items()))
            for predicted_value in predicted.values()
            if tuple(sorted(predicted_value.items())) in gold_values
        ]

        # Find the intersection (minimum counts)
        overlap = sum(
            (Counter(gold_values) & Counter(useful_predicted_values)).values()
        )
        if len(gold_values) == 0:
            logger.error("zero gold values for %s\n\n%s", predicted, gold)
            return 0

        return overlap / len(gold_values)
