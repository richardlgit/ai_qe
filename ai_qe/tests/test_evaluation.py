from ai_qe.evaluation.deterministic import (
    evaluate_exact_value,
    evaluate_subset,
)
from ai_qe.evaluation.models import (
    EvaluationCheck,
    ScenarioEvaluation,
)


def test_subset_evaluation_passes():
    result = evaluate_subset(
        name="Tests",
        actual_values=[
            "TEST-001",
            "TEST-002",
            "TEST-004",
        ],
        expected_values=[
            "TEST-002",
            "TEST-004",
        ],
    )

    assert result.passed is True
    assert result.score == 1.0
    assert result.category == "deterministic"


def test_subset_evaluation_partial_score():
    result = evaluate_subset(
        name="Tests",
        actual_values=[
            "TEST-002",
        ],
        expected_values=[
            "TEST-002",
            "TEST-004",
        ],
    )

    assert result.passed is False
    assert result.score == 0.5


def test_exact_value_evaluation():
    result = evaluate_exact_value(
        name="Risk",
        actual="HIGH",
        expected="HIGH",
    )

    assert result.passed is True
    assert result.score == 1.0


def test_category_scores_are_separated():
    evaluation = ScenarioEvaluation(
        scenario_id="SCN-TEST",
        checks=[
            EvaluationCheck(
                name="Component",
                passed=True,
                score=1.0,
                category="deterministic",
            ),
            EvaluationCheck(
                name="Risk",
                passed=True,
                score=1.0,
                category="deterministic",
            ),
            EvaluationCheck(
                name="AI behavior",
                passed=False,
                score=0.25,
                category="ai",
            ),
            EvaluationCheck(
                name="AI failure mode",
                passed=False,
                score=0.0,
                category="ai",
            ),
        ],
    )

    assert (
        evaluation.score_for_category(
            "deterministic"
        )
        == 1.0
    )

    assert (
        evaluation.score_for_category(
            "ai"
        )
        == 0.125
    )