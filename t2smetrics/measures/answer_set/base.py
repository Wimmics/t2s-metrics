from t2smetrics.core.context import EvaluationContext
from t2smetrics.execution.result_utils import normalize_answer_set_list
from t2smetrics.measures.base import Measure


class AnswerSetMeasure(Measure):
    requires_execution = True

    def _get_answer_json_whitout_normalisation(self, case, context: EvaluationContext):
        gold_result = context.execution_backend.execute(case.golden.raw, return_type="json")
        pred_result = context.execution_backend.execute(case.generated.raw, return_type="json")

        return gold_result, pred_result

    def _get_answer_lists(self, case, context: EvaluationContext):
        gold_result = context.execution_backend.execute(case.golden.raw)
        pred_result = context.execution_backend.execute(case.generated.raw)

        gold_list = normalize_answer_set_list(gold_result)
        pred_list = normalize_answer_set_list(pred_result)

        return gold_list, pred_list

    def _get_answer_sets(self, case, context: EvaluationContext):
        gold_result = context.execution_backend.execute(case.golden.raw)
        pred_result = context.execution_backend.execute(case.generated.raw)

        gold_list = normalize_answer_set_list(gold_result)
        pred_list = normalize_answer_set_list(pred_result)

        return set(gold_list), set(pred_list)

    def _validate(self, gold: set, pred: set) -> bool:
        return True if gold and pred and len(pred) > 0 else False
