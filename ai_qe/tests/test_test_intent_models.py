from ai_qe.agents.models import (
    RepositoryTestAnalysis,
    TestIntentAnalysis as IntentAnalysis,
    TestRelevance as Relevance,
)


def test_repository_test_analysis_schema():
    result = RepositoryTestAnalysis(
    coverage_status="covered",
    related_tests=[
        IntentAnalysis(
            test_name="test_threshold_alert",
            classification=(
                Relevance.REGRESSION_DETECTOR
            ),
            intent=(
                "Verify alert creation "
                "at the threshold."
            ),
            reasoning=(
                "The test expectation conflicts "
                "with the changed equality behavior."
            ),
        )
    ],
    coverage_gaps=[],
    recommended_tests=[],
    confidence=0.95,
    )

    assert (
        result.related_tests[
            0
        ].classification
        == Relevance.REGRESSION_DETECTOR
    )   