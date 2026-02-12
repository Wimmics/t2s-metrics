from rdflib import Graph
from t2smetrics.execution.base import ExecutionBackend


class RDFLibBackend(ExecutionBackend):
    def __init__(self, rdf_file: str, format: str = "turtle"):
        self.graph = Graph()
        self.graph.parse(rdf_file, format=format)

    def execute(self, query: str):
        try:
            result = self.graph.query(query)
        except Exception:
            return None

        if result.type == "ASK":
            return bool(result)

        return [
            tuple(str(v) for v in row)
            for row in result
        ]
