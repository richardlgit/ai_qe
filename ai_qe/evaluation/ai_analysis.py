from ai_qe.agents.models import AIChangeAnalysis
from ai_qe.evaluation.models import EvaluationCheck

CONCEPT_SYNONYMS = {
    "inclusive": [
        "inclusive",
        "includes equality",
        "equal to",
        "<=",
    ],
    "exclusive": [
        "exclusive",
        "strictly less than",
        "<",
    ],
    "below threshold": [
        "below threshold",
        "just below",
        "less than the threshold",
    ],
    "exact threshold": [
        "exact threshold",
        "exactly equal",
        "equal to the threshold",
        "at the threshold",
    ],
    "above threshold": [
        "above threshold",
        "just above",
        "greater than the threshold",
    ],
    "missed alert": [
        "missed alert",
        "alert is suppressed",
        "failure to generate an alert",
        "alerts to be missed",
    ],
    "behavioral_concepts": [
    "threshold",
    "equality",
    "inclusive",
    "exclusive"
    ]
}

def _normalize(text: str) -> str:
    return " ".join(
        text.lower().strip().split()
    )


def _contains_concept(
    text: str,
    concept: str,
) -> bool:
    normalized_text = _normalize(text)
    normalized_concept = _normalize(concept)

    synonyms = CONCEPT_SYNONYMS.get(
        normalized_concept,
        [normalized_concept],
    )

    return any(
        _normalize(term) in normalized_text
        for term in synonyms
    )

def evaluate_concept_group(
    name: str,
    actual_texts: list[str],
    expected_concepts: list[str],
) -> EvaluationCheck:
    combined_text = " ".join(actual_texts)

    matched = [
        concept
        for concept in expected_concepts
        if _contains_concept(
            combined_text,
            concept,
        )
    ]

    if not expected_concepts:
        score = 1.0
    else:
        score = (
            len(matched)
            / len(expected_concepts)
        )

    return EvaluationCheck(
        name=name,
        passed=score >= 0.5,
        score=score,
        category="ai",
        details=(
            f"matched={matched}, "
            f"expected={expected_concepts}"
        ),
    )


def evaluate_ai_analysis(
    analysis: AIChangeAnalysis,
    expectations: dict,
) -> list[EvaluationCheck]:
    checks: list[EvaluationCheck] = []

    behavioral_texts = [
        analysis.change_summary,
        *analysis.behavioral_changes,
    ]

    checks.append(
        evaluate_concept_group(
            name="AI behavioral understanding",
            actual_texts=behavioral_texts,
            expected_concepts=expectations[
                "behavioral_concepts"
            ],
        )
    )

    failure_texts = []

    for failure in (
        analysis.likely_failure_modes
    ):
        failure_texts.append(
            failure.description
        )
        failure_texts.append(
            failure.reasoning
        )

    checks.append(
        evaluate_concept_group(
            name="AI failure mode detection",
            actual_texts=failure_texts,
            expected_concepts=expectations[
                "failure_mode_concepts"
            ],
        )
    )

    checks.append(
        evaluate_concept_group(
            name="AI test focus",
            actual_texts=(
                analysis.recommended_test_focus
            ),
            expected_concepts=expectations[
                "test_focus_concepts"
            ],
        )
    )

    return checks