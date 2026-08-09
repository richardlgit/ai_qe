from pydantic import BaseModel, Field

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