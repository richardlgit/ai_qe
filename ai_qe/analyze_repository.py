import argparse
from pathlib import Path

from ai_qe.change_analysis.repository_analyzer import (
    analyze_repository_change,
)
from dotenv import load_dotenv

from ai_qe.agents.repository_analysis_agent import (
    RepositoryAnalysisAgent,
)
from ai_qe.change_analysis.repository_analyzer import (
    analyze_repository_change,
    analyze_repository_change_with_ai,
    enrich_repository_test_analysis,
    enrich_repository,
)
from ai_qe.llm.factory import create_provider


from ai_qe.repository.test_context import (
    build_test_context,
)

from ai_qe.agents.repository_enrichment_agent import (
    RepositoryEnrichmentAgent,
)



def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(
        description=(
            "Analyze a Git change using "
            "AI-QE discovered repository metadata."
        )
    )

    parser.add_argument(
    "--ai",
    action="store_true",
    help="Add AI QE enrichment",
    )

    parser.add_argument(
        "--repository",
        default=".",
        help="Repository root.",
    )

    parser.add_argument(
        "--base",
        required=True,
    )

    parser.add_argument(
        "--target",
        required=True,
    )

    args = parser.parse_args()


    if args.ai:
        provider = create_provider()

        result = analyze_repository_change(
            repository_root=Path(
                args.repository
            ),
            base_revision=args.base,
            target_revision=args.target,
        )

        test_context = build_test_context(
            repository_root=Path(
                args.repository
            ),
            selected_tests=(
                result.selected_tests
            ),
        )

        enrichment_agent = (
            RepositoryEnrichmentAgent(
                provider=provider
            )
        )

        result = enrich_repository(
            result=result,
            agent=enrichment_agent,
            test_context=test_context,
        )

    else:
        result = analyze_repository_change(
            repository_root=Path(
                args.repository
            ),
            base_revision=args.base,
            target_revision=args.target,
        )

    
    print()
    print(
        "=== AI-QE Repository Change Analysis ==="
    )
    print()

    print("Changed files:")

    for change in result.changes:
        print(
            f"  - {change.file_path}"
        )

    print()
    print("Affected components:")

    if result.affected_components:
        for component in (
            result.affected_components
        ):
            print(
                f"  - {component}"
            )
    else:
        print("  - None discovered")

    print()
    print("Recommended tests:")

    if result.selected_tests:
        for test in result.selected_tests:
            print(f"  - {test}")
    else:
        print("  - None discovered")

    print()
    print("DETERMINISTIC RISK")
    print(
        f"Score: "
        f"{result.risk.score}/100 "
        )
    
    print(
        f"Level: "
        f"{result.risk.level}"
        )

    print(
        f"Release decision: "
        f"{result.risk.decision}"
    )

    print()
    print("Risk reasons:")

    for reason in result.risk.reasons:
        print(f"  - {reason}")

    #AI Analysis
    if result.ai_status == "success":
        ai = result.ai_analysis

        print()
        print("AI QE Analysis:")
        print(
            f"  Summary: "
            f"{ai.change_summary}"
        )

        print()
        print("  Behavioral changes:")
        for item in ai.behavioral_changes:
            print(f"    - {item}")

        print()
        print("  Failure modes:")
        for failure in (
            ai.likely_failure_modes
        ):
            print(
                f"    - [{failure.severity.value}] "
                f"{failure.description}"
            )
            print(
                f"      Reason: "
                f"{failure.reasoning}"
            )

        print()
        print("  Coverage assessment:")
        print(
            f"    {ai.coverage_assessment}"
        )

        print()
        print("  Recommended test focus:")
        for item in (
            ai.recommended_test_focus
        ):
            print(f"    - {item}")

        print()
        print("  QE recommendation:")
        print(
            f"    {ai.qe_recommendation}"
        )

        print()
        print(
            f"  Confidence: "
            f"{ai.confidence:.2f}"
        )

    elif args.ai:
        print()
        print("AI enrichment unavailable.")

        if result.ai_error:
            print(
                f"Reason: {result.ai_error}"
            )

        print(
            "Continuing with deterministic analysis."
        )

    if (
        result.test_analysis_status
        == "success"
    ):
        test_analysis = (
            result.test_analysis
        )

        print()
        print("TEST INTENT ANALYSIS")
        print()

        print(
            f"Coverage status: "
            f"{test_analysis.coverage_status}"
        )

        if test_analysis.related_tests:
            print()
            print("Related tests:")

            for test in (
                test_analysis.related_tests
            ):
                print(
                    f"  - {test.test_name}"
                )

                print(
                    f"    Classification: "
                    f"{test.classification.value}"
                )

                print(
                    f"    Intent: "
                    f"{test.intent}"
                )

                print(
                    f"    Reason: "
                    f"{test.reasoning}"
                )

        if test_analysis.coverage_gaps:
            print()
            print("Coverage gaps:")

            for gap in (
                test_analysis.coverage_gaps
            ):
                print(
                    f"  - {gap}"
                )

        if test_analysis.recommended_tests:
            print()
            print("Recommended tests:")

            for recommendation in (
                test_analysis.recommended_tests
            ):
                print(
                    f"  - {recommendation}"
                )

        print()
        print(
            f"Test analysis confidence: "
            f"{test_analysis.confidence:.2f}"
        )
    elif (
        args.ai
        and result.test_analysis_status
        == "unavailable"
    ):
        print()
        print("Test intent analysis unavailable.")

        if result.test_analysis_error:
            print(
                f"Reason: "
                f"{result.test_analysis_error}"
            )    

if __name__ == "__main__":
    main()