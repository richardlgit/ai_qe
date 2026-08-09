from ai_qe.agents.models import (
    AIChangeAnalysis,
    FailureMode,
)


def test_ai_change_analysis_schema():
    analysis = AIChangeAnalysis(
        change_summary=(
            "Threshold comparison changed."
        ),
        behavioral_changes=[
            "Boundary behavior changed."
        ],
        likely_failure_modes=[
            FailureMode(
                description=(
                    "Threshold value may be missed."
                ),
                severity="high",
                reasoning=(
                    "Comparison excludes equality."
                ),
            )
        ],
        risk_indicators=[
            "Critical conditional changed."
        ],
        recommended_test_focus=[
            "Threshold boundary tests."
        ],
        confidence=0.95,
    )

    assert analysis.confidence == 0.95
    assert len(
        analysis.likely_failure_modes
    ) == 1