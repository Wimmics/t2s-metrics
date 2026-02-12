class LLMBackend:
    def judge(self, prompt: str, timeout: int = 30) -> dict:
        raise NotImplementedError
