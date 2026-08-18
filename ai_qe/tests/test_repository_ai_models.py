from ai_qe.agents.models import (
    FailureMode,
    FailureSeverity,
    RepositoryAIAnalysis,
)


def test_repository_ai_analysis_schema():
    result = RepositoryAIAnalysis(
        change_summary=(
            "Boundary behavior changed."
        ),
        behavioral_changes=[
            "Equality is now handled differently."
        ],
        likely_failure_modes=[
            FailureMode(
                description=(
                    "Boundary alert may be missed."
                ),
                severity=FailureSeverity.HIGH,
                reasoning=(
                    "Equality enters the no-alert path."
                ),
            )
        ],
        coverage_assessment=(
            "Existing tests cover the component "
            "but boundary coverage should be reviewed."
        ),
        recommended_test_focus=[
            "Exact threshold behavior."
        ],
        qe_recommendation=(
            "Review the change before release."
        ),
        confidence=0.95,
    )

    assert result.confidence == 0.95