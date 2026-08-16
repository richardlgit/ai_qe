from dataclasses import dataclass


@dataclass
class RepositoryRisk:
    score: int
    level: str
    decision: str
    reasons: list[str]


def calculate_repository_risk(
    changed_file_count: int,
    affected_component_count: int,
    selected_test_count: int,
) -> RepositoryRisk:
    score = 0
    reasons: list[str] = []

    if changed_file_count > 0:
        score += 20
        reasons.append(
            "Repository contains changed source files."
        )

    if affected_component_count >= 1:
        score += 20
        reasons.append(
            "Change affects discovered application components."
        )

    if affected_component_count >= 3:
        score += 20
        reasons.append(
            "Change spans multiple components."
        )

    if selected_test_count == 0:
        score += 30
        reasons.append(
            "No relevant tests were discovered."
        )

    elif selected_test_count <= 2:
        score += 15
        reasons.append(
            "Limited relevant test coverage was discovered."
        )

    if score >= 70:
        level = "HIGH"
        decision = "BLOCK"
    elif score >= 40:
        level = "MEDIUM"
        decision = "REVIEW"
    else:
        level = "LOW"
        decision = "PASS"

    return RepositoryRisk(
        score=score,
        level=level,
        decision=decision,
        reasons=reasons,
    )