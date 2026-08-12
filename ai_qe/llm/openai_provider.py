from typing import TypeVar

from openai import OpenAI
from pydantic import BaseModel

from ai_qe.llm.base import LLMProvider


T = TypeVar("T", bound=BaseModel)


class OpenAIProvider(LLMProvider):
    def __init__(
        self,
        model: str = "gpt-5-nano",
    ) -> None:
        self.model = model
        self.client = OpenAI()

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )

        return response.output_text

    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T:
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            text_format=response_model,
        )

        if response.output_parsed is None:
            raise RuntimeError(
                "Model returned no structured output."
            )

        return response.output_parsed