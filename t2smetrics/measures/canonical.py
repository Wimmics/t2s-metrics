from t2smetrics.measures.token import TokenF1
from t2smetrics.measures.text_metrics import Bleu4
from t2smetrics.representation.preprocessing import CANONICAL_PREPROCESSOR
from t2smetrics.core.dataset import QueryCase
from t2smetrics.representation.sparql_query import SparqlQuery


class CanonicalF1(TokenF1):
    name = "canonical_f1"

    def compute(self, case: QueryCase, context=None):
        new_case = QueryCase(
            id=case.id,
            golden=SparqlQuery(CANONICAL_PREPROCESSOR.apply(case.golden.raw)),
            generated=SparqlQuery(CANONICAL_PREPROCESSOR.apply(case.generated.raw)),
            order_matters=case.order_matters,
        )
        return super().compute(new_case, context)


class CanonicalBLEU(Bleu4):
    name = "canonical_bleu"
