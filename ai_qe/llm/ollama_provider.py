import time
from typing import TypeVar

from ollama import Client
from pydantic import BaseModel

from ai_qe.llm.base import LLMProvider


T = TypeVar("T", bound=BaseModel)


class OllamaProvider(LLMProvider):
    def __init__(
        self,
        model: str = "deepseek-r1:1.5b",
        host: str = "http://localhost:11434",
    ) -> None:
        self.model = model
        self.client = Client(host=host)

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        print(
            f"Calling local model: {self.model}",
            flush=True,
        )

        start = time.perf_counter()

        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            options={
                "temperature": 0.1,
            },
        )

        elapsed = time.perf_counter() - start

        print(
            f"Model response received in "
            f"{elapsed:.1f} seconds",
            flush=True,
        )

        return response.message.content

    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T:
        print(
            f"Calling local structured model: {self.model}",
            flush=True,
        )

        start = time.perf_counter()

        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            format=response_model.model_json_schema(),
            options={
                "temperature": 0,
            },
        )

        elapsed = time.perf_counter() - start

        print(
            f"Structured response received in "
            f"{elapsed:.1f} seconds",
            flush=True,
        )

        return response_model.model_validate_json(
            response.message.content
        )