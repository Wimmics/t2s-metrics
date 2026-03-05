from t2smetrics.core.dataset import QueryCase
from t2smetrics.execution.result_utils import normalize_query_response
from t2smetrics.measures.base import Measure
from t2smetrics.core.result import EvaluationResult
from t2smetrics.representation.uri_utils import extract_uris


class URIHallucination(Measure):
    name = "uri_hallucination"
    requires_execution = True

    def compute(self, case: QueryCase, context):
        uris: set[str] = extract_uris(case.generated.raw)

        hallucinated_uri_count = 0
        for uri in uris:
            if uri in case.is_uri_hallicinated_map:
                if case.is_uri_hallicinated_map[uri]:
                    hallucinated_uri_count += 1

            else:
                ask_query = f"ASK {{ {{ <{uri}> ?p ?o. }} UNION {{ ?s <{uri}> ?o.}} UNION {{ ?s ?p <{uri}> . }} }}"
                try:
                    response = context.execution_backend.execute(ask_query)
                    exists = normalize_query_response(response)
                    if not exists:
                        hallucinated_uri_count += 1
                except Exception:
                    hallucinated_uri_count += 1

        return EvaluationResult(
            case.id, self.name, hallucinated_uri_count / len(uris) if uris else 0.0
        )
