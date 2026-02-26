import json

from rdflib import Graph
from t2smetrics.execution.base import ExecutionBackend
import logging


logger = logging.getLogger(__name__)


class RDFLibBackend(ExecutionBackend):
    def __init__(self, rdf_file: str, format: str = "turtle"):
        self.graph = Graph()
        self.graph.parse(rdf_file, format=format)

    def execute(self, query: str, return_type: str = "tuples"):
        if return_type not in {"tuples", "json"}:
            raise ValueError(f"Invalid return_type: {return_type}")

        if return_type == "json":
            return self.execute_json(query)
        else:
            return self.execute_tuple(query)

    def execute_tuple(self, query: str):
        try:
            result = self.graph.query(query)
        except Exception as exception:
            logger.error(f"Error executing query: {exception}")
            return None

        if result.type == "ASK":
            return bool(result)

        return [tuple(str(v) for v in row) for row in result]

    def execute_json(self, query: str):
        try:
            result = self.graph.query(query)
            json_dict = json.loads(result.serialize(format="json"))

        except Exception as exception:
            logger.error(f"Error executing query: {exception}")
            return None

        if result.type == "ASK":
            return bool(result)

        return json_dict["results"]["bindings"]
