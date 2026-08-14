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

def evaluate_behavioral_correctness(
    analysis: AIChangeAnalysis,
    expectations: dict,
) -> EvaluationCheck:
    text = " ".join(
        [
            analysis.change_summary,
            *analysis.behavioral_changes,
        ]
    )

    normalized = _normalize(text)

    expected_rules = expectations.get(
        "expected_behavior_rules",
        [],
    )

    matched = []

    # SCN-001 deterministic semantic checks
    if (
        "equal" in normalized
        and "threshold" in normalized
        and (
            "no alert" in normalized
            or "miss" in normalized
            or "suppress" in normalized
        )
    ):
        matched.append(
            "equality boundary regression"
        )

    if (
        "below" in normalized
        and (
            "no alert" in normalized
            or "return none" in normalized
        )
    ):
        matched.append(
            "below-threshold behavior"
        )

    if (
        "above" in normalized
        and "alert" in normalized
    ):
        matched.append(
            "above-threshold behavior"
        )

    score = min(
        len(matched) / 3.0,
        1.0,
    )

    return EvaluationCheck(
        name="AI behavioral correctness",
        passed=score >= 0.5,
        score=score,
        category="ai",
        weight=2.0,
        details=(
            f"matched={matched}, "
            f"ground_truth={expected_rules}"
        ),
    )

def evaluate_failure_reasoning(
    analysis: AIChangeAnalysis,
    expectations: dict,
) -> EvaluationCheck:
    reasoning_text = " ".join(
        failure.reasoning
        for failure
        in analysis.likely_failure_modes
    )

    normalized = _normalize(
        reasoning_text
    )

    matched = []

    if (
        "less than or equal" in normalized
        or "<=" in reasoning_text
    ):
        matched.append(
            "comparison operator"
        )

    if (
        "return none" in normalized
        or "no-alert" in normalized
        or "no alert" in normalized
        or "suppress" in normalized
    ):
        matched.append(
            "no-alert branch"
        )

    if (
        "equal" in normalized
        and "threshold" in normalized
    ):
        matched.append(
            "equality case"
        )

    if (
        "after" in normalized
        and "alert" in normalized
    ):
        matched.append(
            "alert creation flow"
        )

    score = min(
        len(matched) / 3.0,
        1.0,
    )

    return EvaluationCheck(
        name="AI causal reasoning",
        passed=score >= 0.5,
        score=score,
        category="ai",
        weight=2.0,
        details=(
            f"matched={matched}, "
            f"expected="
            f"{expectations.get('expected_causal_concepts', [])}"
        ),
    )

def evaluate_contradictions(
    analysis: AIChangeAnalysis,
    expectations: dict,
) -> EvaluationCheck:
    text_parts = [
        analysis.change_summary,
        *analysis.behavioral_changes,
        *analysis.risk_indicators,
        *analysis.recommended_test_focus,
    ]

    for failure in (
        analysis.likely_failure_modes
    ):
        text_parts.append(
            failure.description
        )
        text_parts.append(
            failure.reasoning
        )

    combined = _normalize(
        " ".join(text_parts)
    )

    patterns = expectations.get(
        "contradiction_patterns",
        [],
    )

    contradictions = [
        pattern
        for pattern in patterns
        if _normalize(pattern)
        in combined
    ]

    if not contradictions:
        score = 1.0
    else:
        score = max(
            0.0,
            1.0 - (
                0.5 * len(contradictions)
            ),
        )

    return EvaluationCheck(
        name="AI contradiction check",
        passed=not contradictions,
        score=score,
        category="ai",
        weight=2.0,
        details=(
            f"contradictions={contradictions}"
        ),
    )

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

    # V2 checks
    checks.append(
        evaluate_behavioral_correctness(
            analysis=analysis,
            expectations=expectations,
        )
    )

    checks.append(
        evaluate_failure_reasoning(
            analysis=analysis,
            expectations=expectations,
        )
    )

    checks.append(
        evaluate_contradictions(
            analysis=analysis,
            expectations=expectations,
        )
    )

    return checks