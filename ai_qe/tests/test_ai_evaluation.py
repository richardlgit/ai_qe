from ai_qe.agents.models import (
    AIChangeAnalysis,
    FailureMode,
    FailureSeverity,
)
from ai_qe.evaluation.ai_analysis import (
    evaluate_ai_analysis,
)


def test_ai_analysis_matches_expected_concepts():
    analysis = AIChangeAnalysis(
        change_summary=(
            "The threshold comparison changed "
            "from inclusive to exclusive."
        ),
        behavioral_changes=[
            "Equality at the threshold "
            "is no longer accepted."
        ],
        likely_failure_modes=[
            FailureMode(
                description=(
                    "A boundary alert may be missed."
                ),
                severity=FailureSeverity.HIGH,
                reasoning=(
                    "Temperature equal to threshold "
                    "does not generate an alert."
                ),
            )
        ],
        risk_indicators=[
            "Critical comparison changed."
        ],
        recommended_test_focus=[
            "below threshold",
            "exact threshold",
            "above threshold",
        ],
        confidence=0.95,
    )

    expectations = {
        "behavioral_concepts": [
            "threshold",
            "equality",
            "inclusive",
            "exclusive",
        ],
        "failure_mode_concepts": [
            "missed",
            "boundary",
            "equal to threshold",
        ],
        "test_focus_concepts": [
            "below threshold",
            "exact threshold",
            "above threshold",
        ],
    }

    checks = evaluate_ai_analysis(
        analysis=analysis,
        expectations=expectations,
    )

    assert len(checks) == 3

    assert all(
        check.passed
        for check in checks
    )

    assert all(
        check.category == "ai"
        for check in checks
    )

def test_ai_analysis_matches_qwen_style_synonyms():
    analysis = AIChangeAnalysis(
        change_summary=(
            "The comparison changed so the condition now "
            "includes equality at the threshold."
        ),
        behavioral_changes=[
            "The previous logic was strictly less than the threshold, "
            "but the new condition suppresses alerts when the value "
            "is exactly equal to the threshold."
        ],
        likely_failure_modes=[
            FailureMode(
                description=(
                    "Failure to generate an alert when the "
                    "temperature reaches the threshold."
                ),
                severity=FailureSeverity.HIGH,
                reasoning=(
                    "The alert is suppressed at the boundary value, "
                    "which can cause alerts to be missed."
                ),
            )
        ],
        risk_indicators=[
            "Boundary comparison changed."
        ],
        recommended_test_focus=[
            "Test just below the threshold.",
            "Test exactly equal to the threshold.",
            "Test just above the threshold.",
        ],
        confidence=0.95,
    )

    expectations = {
        "behavioral_concepts": [
            "threshold",
            "equality",
            "inclusive",
            "exclusive",
        ],
        "failure_mode_concepts": [
            "missed alert",
            "boundary",
            "equal to threshold",
        ],
        "test_focus_concepts": [
            "below threshold",
            "exact threshold",
            "above threshold",
        ],
    }

    checks = evaluate_ai_analysis(
        analysis=analysis,
        expectations=expectations,
    )

    assert len(checks) == 3

    assert all(
        check.passed
        for check in checks
    )

    assert all(
        check.category == "ai"
        for check in checks
    )