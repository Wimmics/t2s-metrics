from concurrent.futures import ThreadPoolExecutor, TimeoutError

from langchain_ollama import ChatOllama
from loguru import logger
from pydantic import BaseModel, Field

from t2smetrics.llm.base import LLMBackend


class JudgeResponse(BaseModel):
    reasoning: str = Field(description="Brief explanation of why this score was given.")
    score: float = Field(description="A score between 0.0 and 1.0", ge=0, le=1)


class OllamaBackend(LLMBackend):
    def __init__(self, model="gemma3:4b"):
        self.model = model

    def judge(self, prompt: str, timeout: int = 30) -> dict:
        llm = ChatOllama(
            temperature=0,
            model=self.model,
            max_tokens=1000,
        )
        structured_llm = llm.with_structured_output(JudgeResponse, method="json_schema")

        def call_llm():
            return structured_llm.invoke(
                input=[
                    {
                        "role": "system",
                        "content": (
                            "You are a SPARQL expert judge. Judge the quality of the SPARQL query "
                            "between 0.0 and 1.0. Verify that the query is syntactically correct "
                            "and adheres to SPARQL standards. Consider the following aspects when judging: "
                            "correctness, efficiency, readability, and adherence to best practices. "
                            "Provide a brief explanation for your score."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ]
            )

        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(call_llm)

        try:
            response = future.result(timeout=timeout)  # Timeout in seconds
        except TimeoutError:
            logger.warning("LLM call timed out.")
            return {"score": None, "raw": "Model call timed out!"}

        return {"score": response.score, "raw": response}
