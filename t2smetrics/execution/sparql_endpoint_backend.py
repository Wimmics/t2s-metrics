from loguru import logger
from SPARQLWrapper import JSON, QueryResult, SPARQLWrapper

from t2smetrics.execution.base import ExecutionBackend
from t2smetrics.execution.result_utils import (
    normalize_query_response,
    safe_append_limit,
)


class SparqlEndpointBackend(ExecutionBackend):
    """Generic SPARQL 1.1 HTTP endpoint backend. Works with Corese, QLever, GraphDB, Fuseki, Virtuoso, Blazegraph, etc."""

    def __init__(
        self,
        endpoint_url: str,
        timeout: int = 60,
        default_graph: str | None = None,
        headers: dict | None = None,
        safe_limit: int = 0,
    ):
        self.endpoint_url = endpoint_url
        self.timeout = timeout
        self.default_graph = default_graph
        self.headers = headers or {}
        self.safe_limit = safe_limit
        self.test_connection()

    def execute(self, query: str) -> "QueryResult.ConvertResult":
        if self.safe_limit != 0:
            query = safe_append_limit(query)

        logger.debug(f"Executing query:\n{query}")
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

    def test_connection(self):
        test_query = "ASK { ?s ?p ?o }"
        try:
            response = self.execute(test_query)
            if response is None:
                raise ConnectionError(
                    f"Failed to connect to SPARQL endpoint at {self.endpoint_url}"
                )
            normalize_query_response(response)
        except Exception as e:
            logger.error(f"Failed when testing connection to SPARQL endpoint: {e}")
            raise ConnectionError(
                f"Failed to connect to SPARQL endpoint at {self.endpoint_url}"
            ) from e
