from ai_qe.change_analysis.risk_engine import (
    calculate_risk,
)


def test_high_risk_change_is_blocked():
    result = calculate_risk(
        component_criticalities=["high"],
        defect_severities=["high"],
        escaped_defect_count=1,
        selected_test_priorities=[
            "critical",
            "critical",
        ],
    )

    assert result.score >= 70
    assert result.level == "HIGH"
    assert result.decision == "BLOCK"