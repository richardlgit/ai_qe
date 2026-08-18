from ai_qe.agents.models import (
    FailureMode,
    FailureSeverity,
    RepositoryAIAnalysis,
    RepositoryAIEnrichment,
    RepositoryTestAnalysis,
    TestIntentAnalysis as IntentAnalysis,
    TestRelevance as Relevance,
)


def test_repository_ai_enrichment_schema():
    enrichment = RepositoryAIEnrichment(
        test_analysis=(
            RepositoryTestAnalysis(
                coverage_status="covered",
                related_tests=[
                    IntentAnalysis(
                        test_name=(
                            "test_threshold"
                        ),
                        classification=(
                            Relevance.REGRESSION_DETECTOR
                        ),
                        intent=(
                            "Verify alert creation "
                            "at the threshold."
                        ),
                        reasoning=(
                            "The existing expectation "
                            "conflicts with the changed "
                            "boundary behavior."
                        ),
                    )
                ],
                coverage_gaps=[],
                recommended_tests=[],
                confidence=0.95,
            )
        ),
        qe_analysis=(
            RepositoryAIAnalysis(
                change_summary=(
                    "Threshold behavior changed."
                ),
                behavioral_changes=[
                    (
                        "Equality now enters "
                        "the no-alert path."
                    )
                ],
                likely_failure_modes=[
                    FailureMode(
                        description=(
                            "Critical alert may "
                            "be missed."
                        ),
                        severity=(
                            FailureSeverity.HIGH
                        ),
                        reasoning=(
                            "The equality case "
                            "is now suppressed."
                        ),
                    )
                ],
                coverage_assessment=(
                    "Existing threshold coverage "
                    "is relevant."
                ),
                recommended_test_focus=[
                    (
                        "Verify expected behavior "
                        "at the threshold."
                    )
                ],
                qe_recommendation=(
                    "Review the implementation "
                    "against the existing test "
                    "expectation."
                ),
                confidence=0.95,
            )
        ),
    )

    assert (
        enrichment.test_analysis
        .related_tests[0]
        .classification
        == Relevance.REGRESSION_DETECTOR
    )

    assert (
        enrichment.qe_analysis.confidence
        == 0.95
    )