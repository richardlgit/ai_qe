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

    assert len(checks) == 6

    concept_checks = {
    check.name: check
    for check in checks
}

    assert (
        concept_checks[
            "AI behavioral understanding"
        ].passed
    )

    assert (
        concept_checks[
            "AI failure mode detection"
        ].passed
    )

    assert (
        concept_checks[
            "AI test focus"
        ].passed
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

    assert len(checks) == 6

    concept_checks = {
    check.name: check
    for check in checks
}

    assert (
        concept_checks[
            "AI behavioral understanding"
        ].passed
    )

    assert (
        concept_checks[
            "AI failure mode detection"
        ].passed
    )

    assert (
        concept_checks[
            "AI test focus"
        ].passed
    )

    assert all(
        check.category == "ai"
        for check in checks
    )

#v2 
def test_ai_evaluation_detects_wrong_control_flow():
    analysis = AIChangeAnalysis(
        change_summary=(
            "The threshold comparison changed."
        ),
        behavioral_changes=[
            (
                "The alert service now generates an alert "
                "when temperature is less than or equal "
                "to the threshold."
            )
        ],
        likely_failure_modes=[
            FailureMode(
                description=(
                    "Boundary behavior changed."
                ),
                severity=FailureSeverity.HIGH,
                reasoning=(
                    "The <= comparison causes additional "
                    "alerts below the threshold."
                ),
            )
        ],
        risk_indicators=[
            "Boundary condition changed."
        ],
        recommended_test_focus=[
            "below threshold",
            "exact threshold",
        ],
        confidence=0.9,
    )

    expectations = {
        "behavioral_concepts": [
            "threshold",
        ],
        "failure_mode_concepts": [
            "boundary",
        ],
        "test_focus_concepts": [
            "below threshold",
            "exact threshold",
        ],
        "expected_behavior_rules": [
            (
                "temperature equal to threshold "
                "must create an alert"
            )
        ],
        "expected_causal_concepts": [
            "equality enters the no-alert branch"
        ],
        "contradiction_patterns": [
            (
                "alert service now generates an alert "
                "when temperature is less than or equal"
            )
        ],
    }


    checks = evaluate_ai_analysis(
        analysis=analysis,
        expectations=expectations,
    )

    contradiction_check = next(
        check
        for check in checks
        if check.name
        == "AI contradiction check"
    )

    assert contradiction_check.passed is False
    assert contradiction_check.score < 1.0

def test_ai_evaluation_rewards_correct_causal_reasoning():
    analysis = AIChangeAnalysis(
        change_summary=(
            "The change expands the no-alert branch "
            "to include equality at the threshold."
        ),
        behavioral_changes=[
            (
                "Temperature equal to the threshold "
                "previously created an alert but now "
                "returns no alert."
            )
        ],
        likely_failure_modes=[
            FailureMode(
                description=(
                    "The critical threshold alert "
                    "can be missed."
                ),
                severity=FailureSeverity.HIGH,
                reasoning=(
                    "Changing < to <= means the equality "
                    "case now enters the return None "
                    "no-alert branch before alert creation."
                ),
            )
        ],
        risk_indicators=[
            "Critical boundary logic changed."
        ],
        recommended_test_focus=[
            "below threshold",
            "exact threshold",
            "above threshold",
        ],
        confidence=0.98,
    )

    expectations = {
        "behavioral_concepts": [
            "threshold",
            "equality",
        ],
        "failure_mode_concepts": [
            "missed alert",
            "boundary",
        ],
        "test_focus_concepts": [
            "below threshold",
            "exact threshold",
            "above threshold",
        ],
        "expected_behavior_rules": [
            (
                "temperature equal to threshold "
                "must create an alert"
            )
        ],
        "expected_causal_concepts": [
            "return none",
            "equality enters the no-alert branch",
        ],
        "contradiction_patterns": [
            (
                "alert is generated when temperature "
                "is less than or equal"
            )
        ],
    }

    checks = evaluate_ai_analysis(
        analysis=analysis,
        expectations=expectations,
    )

    causal = next(
        check
        for check in checks
        if check.name
        == "AI causal reasoning"
    )

    contradiction = next(
        check
        for check in checks
        if check.name
        == "AI contradiction check"
    )

    assert causal.passed is True
    assert contradiction.passed is True