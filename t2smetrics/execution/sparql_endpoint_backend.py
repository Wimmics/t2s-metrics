from SPARQLWrapper import JSON, QueryResult, SPARQLWrapper

from t2smetrics.execution.base import ExecutionBackend


class SparqlEndpointBackend(ExecutionBackend):
    """Generic SPARQL 1.1 HTTP endpoint backend.
    Works with Corese, QLever, GraphDB, Fuseki, Virtuoso, Blazegraph, etc.
    """

    def __init__(
        self,
        endpoint_url: str,
        timeout: int = 60,
        default_graph: str | None = None,
        headers: dict | None = None,
    ):
        self.endpoint_url = endpoint_url
        self.timeout = timeout
        self.default_graph = default_graph
        self.headers = headers or {}

    def execute(self, query: str) -> "QueryResult.ConvertResult":

        sparql = SPARQLWrapper(self.endpoint_url)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        sparql.setTimeout(self.timeout)

        if self.default_graph:
            sparql.addDefaultGraph(self.default_graph)

        for k, v in self.headers.items():
            sparql.addCustomHttpHeader(k, v)

        try:
            response = sparql.query().convert()
        except Exception:
            return None

        return response
