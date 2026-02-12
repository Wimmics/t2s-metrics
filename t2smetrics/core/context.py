class EvaluationContext:
    def __init__(
        self,
        execution_backend=None,
        llm_backend=None,
        cache=None,
    ):
        self.execution_backend = execution_backend
        self.llm_backend = llm_backend
        self.cache = cache
