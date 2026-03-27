import json

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

    def judge(self, prompt: str, timeout: int = 30, num_predict: int = 1000) -> dict:

        llm = ChatOllama(
            format="json",
            temperature=0,
            model=self.model,
            validate_model_on_init=True,
            num_predict=num_predict,
            timeout=timeout,
        )
        try:
            response: dict = json.loads(
                llm.invoke(
                    "You are a SPARQL expert judge. Judge the quality of the SPARQL query "
                    "between 0.0 and 1.0. Verify that the query is syntactically correct "
                    "and adheres to SPARQL standards. Consider the following aspects when judging: "
                    "correctness, efficiency, readability, and adherence to best practices. "
                    "Provide a brief explanation for your score."
                    "Use two keys: 'score' for the score and 'reasoning' for the explanation."
                    f"{prompt}"
                ).content
            )
            return {
                "score": response["score"],
                "reasoning": response["reasoning"],
                "raw": response,
            }
        except (KeyError, AttributeError, json.JSONDecodeError) as e:
            logger.error(
                f"Failed to extract score and reasoning from LLM response. Error: {e}"
            )
            return {"score": 0, "raw": "Failed to extract score and reasoning."}
