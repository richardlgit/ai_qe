from ai_qe.agents.models import (
    ChangeCoverageAnalysis,
    ExistingTestGap,
    NewTestRequirement,
)


def test_change_coverage_analysis_schema():
    result = ChangeCoverageAnalysis(
        summary=(
            "User creation now returns "
            "a generated UUID."
        ),
        coverage_status="partial",
        existing_test_changes=[
            ExistingTestGap(
                test_name=(
                    "test_create_get_user"
                ),
                gap=(
                    "The test still uses "
                    "the fixture id."
                ),
                suggested_change=(
                    "Use the UUID returned "
                    "by POST for GET."
                ),
            )
        ],
        new_tests_required=[
            NewTestRequirement(
                behavior=(
                    "Duplicate user creation"
                ),
                assertions=[
                    "Returns HTTP 409.",
                    "Transaction is rolled back.",
                ],
            )
        ],
        unaffected_tests=[
            "test_root"
        ],
        remaining_risks=[],
        confidence=0.95,
    )

    assert (
        result.coverage_status
        == "partial"
    )

    assert len(
        result.existing_test_changes
    ) == 1