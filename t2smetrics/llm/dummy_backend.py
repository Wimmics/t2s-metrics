from t2smetrics.llm.base import LLMBackend


class DummyLLMBackend(LLMBackend):
    def judge(self, prompt: str) -> dict:
        # Always return neutral judgment
        return {
            "score": 0.5,
            "reason": "Dummy backend"
        }
