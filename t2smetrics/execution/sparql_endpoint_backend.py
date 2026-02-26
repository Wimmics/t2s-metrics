from SPARQLWrapper import SPARQLWrapper, JSON
from t2smetrics.execution.base import ExecutionBackend


class SparqlEndpointBackend(ExecutionBackend):
    """
    Generic SPARQL 1.1 HTTP endpoint backend.
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

    def execute(self, query: str, return_type: str = "tuples"):

        if return_type not in {"tuples", "json"}:
            raise ValueError(f"Invalid return_type: {return_type}")

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

        # ASK queries
        if "boolean" in response:
            return bool(response["boolean"])

        # SELECT queries
        vars_ = response["head"]["vars"]
        rows = []

        if return_type == "json":
            return response["results"]["bindings"]

        else:
            for binding in response["results"]["bindings"]:
                if binding is None:
                    continue
                elif len(binding) == 0:
                    continue
                row = tuple(
                    binding[var]["value"] if var in binding else None for var in vars_
                )
                rows.append(row)

            return rows
