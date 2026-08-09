from dataclasses import dataclass


CRITICALITY_SCORES = {
    "critical": 30,
    "high": 25,
    "medium": 15,
    "low": 5,
}

DEFECT_SEVERITY_SCORES = {
    "critical": 25,
    "high": 20,
    "medium": 10,
    "low": 5,
}

TEST_PRIORITY_SCORES = {
    "critical": 15,
    "high": 10,
    "medium": 5,
    "low": 2,
}


@dataclass
class RiskAssessment:
    score: int
    level: str
    decision: str
    reasons: list[str]


def calculate_risk(
    component_criticalities: list[str],
    defect_severities: list[str],
    escaped_defect_count: int,
    selected_test_priorities: list[str],
) -> RiskAssessment:
    reasons: list[str] = []

    score = 0

    if component_criticalities:
        component_score = max(
            CRITICALITY_SCORES.get(
                criticality,
                0,
            )
            for criticality
            in component_criticalities
        )

        score += component_score

        reasons.append(
            "Affected component criticality "
            f"contributed {component_score} points."
        )

    if defect_severities:
        defect_score = max(
            DEFECT_SEVERITY_SCORES.get(
                severity,
                0,
            )
            for severity in defect_severities
        )

        score += defect_score

        reasons.append(
            "Historical defect severity "
            f"contributed {defect_score} points."
        )

    if escaped_defect_count:
        escaped_score = min(
            escaped_defect_count * 15,
            30,
        )

        score += escaped_score

        reasons.append(
            "Prior production escapes "
            f"contributed {escaped_score} points."
        )

    critical_tests = sum(
        1
        for priority in selected_test_priorities
        if priority == "critical"
    )

    if critical_tests:
        test_score = min(
            critical_tests * 10,
            20,
        )

        score += test_score

        reasons.append(
            "Critical regression exposure "
            f"contributed {test_score} points."
        )

    score = min(score, 100)

    if score >= 70:
        level = "HIGH"
        decision = "BLOCK"

    elif score >= 40:
        level = "MEDIUM"
        decision = (
            "HUMAN_REVIEW_REQUIRED"
        )

    else:
        level = "LOW"
        decision = "APPROVE"

    return RiskAssessment(
        score=score,
        level=level,
        decision=decision,
        reasons=reasons,
    )