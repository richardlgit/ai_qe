from enum import Enum

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)

from pydantic import BaseModel, Field

class TestRelevance(str, Enum):
    REGRESSION_DETECTOR = "regression_detector"
    RELEVANT_COMPLETE = "relevant_complete"
    RELEVANT_INCOMPLETE = "relevant_incomplete"
    POSSIBLY_OBSOLETE = "possibly_obsolete"
    REDUNDANT = "redundant"
    UNAFFECTED = "unaffected"

class TestIntentAnalysis(BaseModel):
    test_name: str

    classification: TestRelevance

    intent: str = Field(
        min_length=5
    )

    reasoning: str = Field(
        min_length=10
    )

class RepositoryAIEnrichment(BaseModel):
    # test_analysis: RepositoryTestAnalysis
    # qe_analysis: RepositoryAIAnalysis
    coverage_analysis: ChangeCoverageAnalysis

class RepositoryTestAnalysis(BaseModel):
    coverage_status: str

    related_tests: list[TestIntentAnalysis] = Field(
        default_factory=list
    )

    coverage_gaps: list[str] = Field(
        default_factory=list
    )

    recommended_tests: list[str] = Field(
        default_factory=list
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

class RepositoryAIAnalysis(BaseModel):
    change_summary: str = Field(
        min_length=10
    )

    behavioral_changes: list[str] = Field(
        min_length=1
    )

    likely_failure_modes: list[FailureMode] = Field(
        min_length=1
    )

    coverage_assessment: str = Field(
        min_length=10
    )

    recommended_test_focus: list[str] = Field(
        min_length=1
    )

    qe_recommendation: str = Field(
        min_length=10
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

class FailureSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FailureMode(BaseModel):
    description: str = Field(
        min_length=5
    )

    severity: FailureSeverity

    reasoning: str = Field(
        min_length=5
    )


class AIChangeAnalysis(BaseModel):
    change_summary: str = Field(
        min_length=10
    )

    behavioral_changes: list[str] = Field(
        min_length=1
    )

    likely_failure_modes: list[
        FailureMode
    ] = Field(
        min_length=1
    )

    risk_indicators: list[str] = Field(
        min_length=1
    )

    recommended_test_focus: list[str] = Field(
        min_length=2
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

class ExistingTestGap(BaseModel):
    test_name: str

    gap: str = Field(
        min_length=5
    )

    suggested_change: str = Field(
        min_length=5
    )


class NewTestRequirement(BaseModel):
    behavior: str = Field(
        min_length=5
    )

    assertions: list[str] = Field(
        min_length=1
    )


class ChangeCoverageAnalysis(BaseModel):
    summary: str = Field(
        min_length=10
    )

    coverage_status: str

    existing_test_changes: list[
        ExistingTestGap
    ] = Field(
        default_factory=list
    )

    new_tests_required: list[
        NewTestRequirement
    ] = Field(
        default_factory=list
    )

    unaffected_tests: list[str] = Field(
        default_factory=list
    )

    remaining_risks: list[str] = Field(
        default_factory=list
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )