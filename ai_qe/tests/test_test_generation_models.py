from ai_qe.agents.models import (
    AITestGeneration,
    FailureSeverity,
    GeneratedTest,
)


def test_ai_test_generation_schema():
    generated = AITestGeneration(
        test_strategy_summary=(
            "Validate threshold boundaries."
        ),
        generated_tests=[
            GeneratedTest(
                name=(
                    "test_temperature_boundary"
                ),
                purpose=(
                    "Validate exact threshold."
                ),
                test_type="api",
                priority=(
                    FailureSeverity.CRITICAL
                ),
                target_file=(
                    "edgepulse/tests/api/"
                    "test_alerts.py"
                ),
                code=(
                    "def test_temperature_boundary():"
                    "\n    assert True"
                ),
            )
        ],
        coverage_gaps=[
            "Boundary coverage"
        ],
        assumptions=[],
        confidence=0.95,
    )

    assert len(
        generated.generated_tests
    ) == 1

    assert (
        generated.generated_tests[
            0
        ].priority
        == FailureSeverity.CRITICAL
    )