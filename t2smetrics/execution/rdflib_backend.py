import json

from loguru import logger
from rdflib import Graph

from t2smetrics.execution.base import ExecutionBackend
from t2smetrics.execution.result_utils import safe_append_limit


class RDFLibBackend(ExecutionBackend):
    def __init__(self, rdf_file: str, format: str = "turtle", safe_limit: int = 0):
        self.graph = Graph()
        self.safe_limit = safe_limit
        try:
            self.graph.parse(rdf_file, format=format)
        except Exception as exception:
            logger.error(f"Error parsing RDF file: {exception}")
            raise ValueError(
                f"Failed to parse RDF file: {rdf_file}. Please ensure the file exists and is in the correct format ({format})."
            ) from exception

    def execute(self, query: str):
        try:
            if self.safe_limit != 0:
                query = safe_append_limit(query)
            result = self.graph.query(query)
            json_dict = json.loads(result.serialize(format="json"))
            return json_dict

        except Exception as exception:
            logger.error(f"Error executing query: {exception}")
            return None
