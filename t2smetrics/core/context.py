class EvaluationContext:
    def __init__(
        self,
        execution_backend=None,
        llm_backend=None,
        cache_result_sets: bool = True,
    ):
        self.execution_backend = execution_backend
        self.llm_backend = llm_backend
        self.cache_result_sets = cache_result_sets
