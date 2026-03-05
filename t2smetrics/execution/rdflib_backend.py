import json

from rdflib import Graph
from t2smetrics.execution.base import ExecutionBackend
import logging


logger = logging.getLogger(__name__)


class RDFLibBackend(ExecutionBackend):
    def __init__(self, rdf_file: str, format: str = "turtle"):
        self.graph = Graph()
        self.graph.parse(rdf_file, format=format)

    def execute(self, query: str):
        try:
            result = self.graph.query(query)
            json_dict = json.loads(result.serialize(format="json"))
            return json_dict

        except Exception as exception:
            logger.error(f"Error executing query: {exception}")
            return None
