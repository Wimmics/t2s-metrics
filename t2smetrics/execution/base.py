class ExecutionBackend:
    def execute(self, query: str, return_type: str = "tuples"):
        raise NotImplementedError
