from typing import TypeVar

from openai import OpenAI
from pydantic import BaseModel

from ai_qe.llm.base import LLMProvider
import time


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
        start_time = time.perf_counter()

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
        elapsed_seconds = (time.perf_counter() - start_time)

        if response.output_parsed is None:
            raise RuntimeError(
                "Model returned no structured output."
            )

        usage = response.usage

        if usage is not None:
            print()
            print("AI MODEL USAGE")
            print(f"  Model: {self.model}")
            print(
                f"  Input tokens: "
                f"{usage.input_tokens:,}"
            )
            print(
                f"  Output tokens: "
                f"{usage.output_tokens:,}"
            )
            print(
                f"  Total tokens: "
                f"{usage.total_tokens:,}"
            )
            print(
                f"  Latency: "
                f"{elapsed_seconds:.1f}s"
            )

        cached_tokens = 0

        if (
            usage is not None
            and usage.input_tokens_details
            is not None
        ):
            cached_tokens = (
                usage.input_tokens_details.cached_tokens
                or 0
            )

            print(
                f"  Cached input tokens: "
                f"{cached_tokens:,}"
            )

        return response.output_parsed