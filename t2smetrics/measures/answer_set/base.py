from t2smetrics.core.context import EvaluationContext
from t2smetrics.core.dataset import _NOT_CACHED, QueryCase
from t2smetrics.execution.result_utils import (
    normalize_answer_set_list,
    normalize_query_response,
)
from t2smetrics.measures.base import Measure


class AnswerSetMeasure(Measure):
    requires_execution = True

    def _get_answer_json_whitout_normalisation(
        self, case: QueryCase, context: EvaluationContext
    ):
        if context.cache_result_sets:

            if case.generated_response is not _NOT_CACHED:
                # print("Using cached predicted result for case", case.id)
                pred_response = case.generated_response
            else:
                pred_response = context.execution_backend.execute(case.generated.raw)
                case.generated_response = pred_response

            if case.golden_response is not _NOT_CACHED:
                # print("Using cached golden result for case", case.id)
                gold_response = case.golden_response
            else:
                gold_response = context.execution_backend.execute(case.golden.raw)
                case.golden_response = gold_response
        else:
            pred_response = context.execution_backend.execute(case.generated.raw)
            gold_response = context.execution_backend.execute(case.golden.raw)

        gold_result = normalize_query_response(gold_response, "json")
        pred_result = normalize_query_response(pred_response, "json")
        return gold_result, pred_result

    def _get_answer_lists(self, case: QueryCase, context: EvaluationContext):
        if context.cache_result_sets:

            if case.generated_response is not _NOT_CACHED:
                # print("Using cached predicted result for case", case.id)
                pred_response = case.generated_response
            else:
                pred_response = context.execution_backend.execute(case.generated.raw)
                case.generated_response = pred_response

            if case.golden_response is not _NOT_CACHED:
                # print("Using cached golden result for case", case.id)
                gold_response = case.golden_response
            else:
                gold_response = context.execution_backend.execute(case.golden.raw)
                case.golden_response = gold_response
        else:
            pred_response = context.execution_backend.execute(case.generated.raw)
            gold_response = context.execution_backend.execute(case.golden.raw)

        gold_list = normalize_answer_set_list(normalize_query_response(gold_response))
        pred_list = normalize_answer_set_list(normalize_query_response(pred_response))

        return gold_list, pred_list

    def _get_answer_sets(self, case: QueryCase, context: EvaluationContext):
        gold_list, pred_list = self._get_answer_lists(case, context)
        return set(gold_list), set(pred_list)

    def _validate(self, gold: set, pred: set) -> bool:
        return True if gold and pred and len(pred) > 0 else False
