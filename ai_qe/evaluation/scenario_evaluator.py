from ai_qe.change_analysis.analyzer import (
    ChangeAnalysisResult,
)
from ai_qe.datasets import loader as load
from ai_qe.evaluation.deterministic import (
    evaluate_exact_value,
    evaluate_subset,
)
from ai_qe.evaluation.models import (
    ScenarioEvaluation,
)
from ai_qe.evaluation.ai_analysis import (
    evaluate_ai_analysis,
)


def evaluate_scenario(
    scenario_id: str,
    analysis: ChangeAnalysisResult,
) -> ScenarioEvaluation:
    expected = (
        load.load_changed_scenario_expected(
            scenario_id
        )
    )

    evaluation = ScenarioEvaluation(
        scenario_id=scenario_id
    )

    evaluation.checks.append(
        evaluate_subset(
            name="Affected components",
            actual_values=[
                component.name
                for component
                in analysis.affected_components
            ],
            expected_values=expected[
                "expected_affected_components"
            ],
        )
    )

    evaluation.checks.append(
        evaluate_subset(
            name="Test selection",
            actual_values=[
                test.test_id
                for test
                in analysis.selected_tests
            ],
            expected_values=expected[
                "expected_test_selection"
            ],
        )
    )

    evaluation.checks.append(
        evaluate_subset(
            name="Historical defects",
            actual_values=[
                defect.defect_id
                for defect
                in analysis.historical_defects
            ],
            expected_values=expected[
                "expected_historical_defects"
            ],
        )
    )

    evaluation.checks.append(
        evaluate_exact_value(
            name="Risk level",
            actual=analysis.risk.level,
            expected=expected[
                "expected_risk_level"
            ],
        )
    )

    evaluation.checks.append(
        evaluate_exact_value(
            name="Release decision",
            actual=analysis.risk.decision,
            expected=expected[
                "expected_release_decision"
            ],
        )
    )

    ai_expectations = expected.get(
        "ai_expectations"
    )

    if (
        ai_expectations is not None
        and analysis.ai_analysis is not None
    ):
        print()
        print("----- AI Debug -----")
        print(
            "Summary:",
            analysis.ai_analysis.change_summary,
        )

        print(
            "Behavioral changes:",
            analysis.ai_analysis.behavioral_changes,
        )

        print(
            "Failure modes:",
            [
                {
                    "description": failure.description,
                    "reasoning": failure.reasoning,
                }
                for failure
                in analysis.ai_analysis.likely_failure_modes
            ],
        )

        print(
            "Test focus:",
            analysis.ai_analysis.recommended_test_focus,
        )

        print("--------------------")
        print()
        evaluation.checks.extend(
            evaluate_ai_analysis(
                analysis=analysis.ai_analysis,
                expectations=ai_expectations,
            )
        )
    
    return evaluation