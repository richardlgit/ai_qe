from enum import Enum

from pydantic import BaseModel, Field, field_validator


class FailureSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FailureMode(BaseModel):
    description: str
    severity: FailureSeverity
    reasoning: str


class AIChangeAnalysis(BaseModel):
    change_summary: str

    behavioral_changes: list[str] = Field(
        default_factory=list
    )

    likely_failure_modes: list[FailureMode] = Field(
        default_factory=list
    )

    risk_indicators: list[str] = Field(
        default_factory=list
    )

    recommended_test_focus: list[str] = Field(
        default_factory=list
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    @field_validator("confidence", mode="before")
    @classmethod
    def normalize_confidence(
        cls,
        value: float | int,
    ) -> float:
        numeric_value = float(value)

        if 1 < numeric_value <= 100:
            return numeric_value / 100.0

        return numeric_value
    
class GeneratedTest(BaseModel):
    name: str
    purpose: str
    test_type: str
    priority: FailureSeverity
    target_file: str
    code: str


class AITestGeneration(BaseModel):
    test_strategy_summary: str

    generated_tests: list[GeneratedTest] = Field(
        min_length=1
    )

    coverage_gaps: list[str] = Field(
        default_factory=list
    )

    assumptions: list[str] = Field(
        default_factory=list
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    @field_validator(
        "confidence",
        mode="before",
    )
    @classmethod
    def normalize_test_confidence(
        cls,
        value: float | int,
    ) -> float:
        numeric_value = float(value)

        if 1 < numeric_value <= 100:
            return numeric_value / 100.0

        return numeric_value