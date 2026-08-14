from ai_qe.evaluation.models import (
    EvaluationCheck,
)


def evaluate_subset(
    name: str,
    actual_values: list[str],
    expected_values: list[str],
) -> EvaluationCheck:
    actual = set(actual_values)
    expected = set(expected_values)

    if not expected:
        score = 1.0
    else:
        score = (
            len(actual.intersection(expected))
            / len(expected)
        )

    return EvaluationCheck(
        name=name,
        passed=score == 1.0,
        score=score,
        details=(
            f"expected={sorted(expected)}, "
            f"actual={sorted(actual)}"
        ),
    )


def evaluate_exact_value(
    name: str,
    actual: str,
    expected: str,
) -> EvaluationCheck:
    actual_normalized = actual.strip().upper()
    expected_normalized = expected.strip().upper()

    passed = (
        actual_normalized
        == expected_normalized
    )

    return EvaluationCheck(
        name=name,
        passed=passed,
        score=1.0 if passed else 0.0,
        details=(
            f"expected={expected_normalized}, "
            f"actual={actual_normalized}"
        ),
    )