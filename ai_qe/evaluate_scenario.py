import argparse

from ai_qe.change_analysis.analyzer import (
    analyze_change,
)
from ai_qe.datasets import loader as load
from ai_qe.evaluation.scenario_evaluator import (
    evaluate_scenario,
)

from dotenv import load_dotenv

from ai_qe.agents.change_analysis_agent import (
    ChangeAnalysisAgent,
)
from ai_qe.change_analysis.analyzer import (
    analyze_change,
    analyze_change_with_ai,
)
from ai_qe.llm.factory import (
    create_provider,
)

def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate QE analysis against "
            "known scenario ground truth."
        )
    )

    parser.add_argument(
        "--scenario",
        required=True,
    )

    parser.add_argument(
        "--base",
        required=True,
    )

    parser.add_argument(
        "--target",
        required=True,
    )

    parser.add_argument(
    "--ai",
    action="store_true",
    help="Include AI analysis evaluation",
)

    args = parser.parse_args()

    scenario = load.load_changed_scenario(
        args.scenario
    )

    if args.ai:
        provider = create_provider()

        agent = ChangeAnalysisAgent(
            provider=provider
        )

        analysis = analyze_change_with_ai(
            base_revision=args.base,
            target_revision=args.target,
            agent=agent,
        )

    else:
        analysis = analyze_change(
            base_revision=args.base,
            target_revision=args.target,
        )

    evaluation = evaluate_scenario(
        scenario_id=args.scenario,
        analysis=analysis,
    )

    print()
    print(
        "=== EdgePulse QE Scenario Evaluation ==="
    )
    print()

    print(
        f"Scenario: "
        f"{scenario['scenario_id']} - "
        f"{scenario['title']}"
    )

    print()

    for check in evaluation.checks:
        status = (
            "PASS"
            if check.passed
            else "FAIL"
        )

        print(
            f"{check.name:24} "
            f"{status:5} "
            f"{check.score * 100:6.1f}%"
        )

    print()

    deterministic_score = (
        evaluation.score_for_category(
        "deterministic"
    )
    )

    print(
        "Deterministic score: "
        f"{deterministic_score * 100:.1f}%"
    )

    if args.ai:
        ai_score = (
            evaluation.score_for_category(
                "ai"
            )
        )

        print(
            "AI analysis score:   "
            f"{ai_score * 100:.1f}%"
        )

    print(
        "Combined score:      "
        f"{evaluation.overall_score * 100:.1f}%"
    )


if __name__ == "__main__":
    main()