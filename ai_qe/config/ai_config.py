from dataclasses import dataclass
import os

from enum import Enum


def __str__(self) -> str:
    return (
        f"{self.provider.value}"
        f" ({self.model})"
    )

class AIProvider(str, Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"

@dataclass(frozen=True)
class AIConfig:
    provider: AIProvider
    model: str
    temperature: float
    timeout_seconds: int

    @classmethod
    def from_env(cls) -> "AIConfig":
        provider = AIProvider(
            os.getenv(
                "AI_QE_PROVIDER",
                "ollama",
            ).lower()
        )

        default_models = {
            AIProvider.OLLAMA: "deepseek-r1:1.5b",
            AIProvider.OPENAI: "gpt-5-nano",
        }

        return cls(
            provider=provider,
            model=os.getenv(
                "AI_QE_MODEL",
                default_models[provider],
            ),
            temperature=float(
                os.getenv(
                    "AI_QE_TEMPERATURE",
                    "0.0",
                )
            ),
            timeout_seconds=int(
                os.getenv(
                    "AI_QE_TIMEOUT_SECONDS",
                    "300",
                )
            ),
        )