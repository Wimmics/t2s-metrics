from t2smetrics.measures.base import Measure
from t2smetrics.core.result import EvaluationResult
from t2smetrics.representation.uri_utils import extract_uris


class URIHallucination(Measure):
    name = "uri_hallucination"
    requires_execution = True

    def compute(self, case, context):
        uris = extract_uris(case.generated.raw)

        hallucinated = False
        for uri in uris:
            # ask_query = f"ASK {{ <{uri}> ?p ?o }}"
            ask_query = f"ASK {{ {{ <{uri}> ?p ?o. }} UNION {{ ?s <{uri}> ?o.}} UNION {{ ?s ?p <{uri}> . }} }}"
            try:
                exists = context.execution_backend.execute(ask_query)
                if not exists:
                    hallucinated = True
                    break
            except Exception:
                hallucinated = True
                break

        return EvaluationResult(case.id, self.name, float(hallucinated))
