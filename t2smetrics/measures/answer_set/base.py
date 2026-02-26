from t2smetrics.core.context import EvaluationContext
from t2smetrics.execution.result_utils import normalize_answer_set_set
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

        gold_set = normalize_answer_set_set(gold_result)
        pred_set = normalize_answer_set_set(pred_result)

        return gold_set, pred_set

    def _get_answer_sets(self, case, context: EvaluationContext):
        gold_result = context.execution_backend.execute(case.golden.raw)
        pred_result = context.execution_backend.execute(case.generated.raw)

        gold_set = normalize_answer_set_set(gold_result)
        pred_set = normalize_answer_set_set(pred_result)

        return set(gold_set), set(pred_set)

    def _validate(self, gold: set, pred: set) -> bool:
        return True if gold and pred and len(pred) > 0 else False
