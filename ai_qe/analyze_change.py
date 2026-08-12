import argparse
import json
from dataclasses import asdict

from dotenv import load_dotenv

load_dotenv()

from ai_qe.change_analysis.analyzer import (
    analyze_change,
)

from ai_qe.agents.change_analysis_agent import (
    ChangeAnalysisAgent,
)
from ai_qe.change_analysis.analyzer import (
    analyze_change,
    analyze_change_with_ai,
)

from ai_qe.llm.ollama_provider import (
    OllamaProvider,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze a Git change for "
            "Quality Engineering risk."
        )
    )

    parser.add_argument(
    "--ai",
    action="store_true",
    help="Enrich deterministic analysis with LLM reasoning",
    )
    
    parser.add_argument(
        "--base",
        required=True,
        help="Base Git revision",
    )

    parser.add_argument(
        "--target",
        required=True,
        help="Target Git revision",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON",
    )

    args = parser.parse_args()

    if args.ai:
        from ai_qe.llm.factory import (
            create_provider,
        )

        provider = create_provider()

        agent = ChangeAnalysisAgent(
            provider=provider,
        )

        result = analyze_change_with_ai(
            base_revision=args.base,
            target_revision=args.target,
            agent=agent,
        )
    else:
        result = analyze_change(
            base_revision=args.base,
            target_revision=args.target,
        )

    if args.json:
        print(
            json.dumps(
                asdict(result),
                indent=2,
            )
        )
        return
    
    print()
    print("=== EdgePulse QE Change Analysis ===")
    print()

    print("Changed files:")
    for change in result.changes:
        print(
            f"  - {change.file_path}"
        )

    print()
    print("Affected components:")
    for component in (
        result.affected_components
    ):
        print(
            f"  - {component.name} "
            f"({component.criticality})"
        )

    print()
    print("Selected tests:")
    for test in result.selected_tests:
        print(
            f"  - {test.test_id}: "
            f"{test.name} "
            f"[{test.priority}]"
        )

    print()
    print("Historical defects:")
    for defect in (
        result.historical_defects
    ):
        print(
            f"  - {defect.defect_id}: "
            f"{defect.title}"
        )


    if result.ai_analysis is not None:
        print()
        print("AI Change Analysis:")
        print(
            f"  Summary: "
            f"{result.ai_analysis.change_summary}"
        )

        print()
        print("  Behavioral changes:")

        for change in (
            result.ai_analysis.behavioral_changes
        ):
            print(
                f"    - {change}"
            )

        print()
        print("  Likely failure modes:")

        for failure in (
            result.ai_analysis.likely_failure_modes
        ):
            print(
                f"    - [{failure.severity}] "
                f"{failure.description}"
            )

            print(
                f"      Reason: "
                f"{failure.reasoning}"
            )

        print()
        print("  Recommended test focus:")

        for focus in (
            result.ai_analysis.recommended_test_focus
        ):
            print(
                f"    - {focus}"
            )

        print()
        print(
            "  Confidence: "
            f"{result.ai_analysis.confidence:.2f}"
        )

    print()
    print(
        f"Risk score: {result.risk.score}/100"
    )
    print(
        f"Risk level: {result.risk.level}"
    )
    print(
        f"Release decision: "
        f"{result.risk.decision}"
    )

    print()
    print("Risk reasons:")

    for reason in result.risk.reasons:
        print(
            f"  - {reason}"
        )


if __name__ == "__main__":
    main()