from ai_qe.change_analysis.repository_risk import (
    calculate_repository_risk,
)


def test_change_with_tests_has_lower_risk():
    risk = calculate_repository_risk(
        changed_file_count=1,
        affected_component_count=1,
        selected_test_count=5,
    )

    assert risk.score >= 40
    assert risk.level == "MEDIUM"
    assert risk.decision == "REVIEW"


def test_change_without_tests_has_higher_risk():
    risk = calculate_repository_risk(
        changed_file_count=1,
        affected_component_count=1,
        selected_test_count=0,
    )

    assert risk.score >= 70
    assert risk.level == "HIGH"
    assert risk.decision == "BLOCK"