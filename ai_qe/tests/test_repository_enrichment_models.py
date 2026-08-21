from ai_qe.agents.models import (
    ChangeCoverageAnalysis,
    ExistingTestGap,
    NewTestRequirement,
    RepositoryAIEnrichment,
)


def test_repository_ai_enrichment_schema():
    enrichment = RepositoryAIEnrichment(
        coverage_analysis=(
            ChangeCoverageAnalysis(
                summary=(
                    "User creation now uses UUID "
                    "identifiers and a typed response."
                ),
                coverage_status="partial",
                existing_test_changes=[
                    ExistingTestGap(
                        test_name=(
                            "test_create_get_user"
                        ),
                        gap=(
                            "The test still relies on "
                            "the removed fixture id."
                        ),
                        suggested_change=(
                            "Use the UUID returned by "
                            "the create response."
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
                            (
                                "The transaction is "
                                "rolled back."
                            ),
                        ],
                    )
                ],
                unaffected_tests=[
                    "test_root",
                ],
                remaining_risks=[],
                confidence=0.95,
            )
        )
    )

    assert (
        enrichment.coverage_analysis
        .coverage_status
        == "partial"
    )

    assert (
        enrichment.coverage_analysis
        .existing_test_changes[0]
        .test_name
        == "test_create_get_user"
    )

    assert (
        enrichment.coverage_analysis
        .confidence
        == 0.95
    )