import argparse

from dotenv import load_dotenv

from ai_qe.agents.test_generation_agent import (
    TestGenerationAgent,
)
from ai_qe.change_analysis.test_generation import (
    generate_tests_for_change,
)
from ai_qe.llm.factory import (
    create_provider,
)


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(
        description=(
            "Generate AI-assisted pytest suggestions "
            "for a Git change."
        )
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

    args = parser.parse_args()

    provider = create_provider()

    agent = TestGenerationAgent(
        provider=provider
    )

    result = generate_tests_for_change(
        base_revision=args.base,
        target_revision=args.target,
        agent=agent,
    )

    print()
    print(
        "=== EdgePulse AI Test Generation ==="
    )
    print()

    print("Changed files:")

    for change in result.analysis.changes:
        print(
            f"  - {change.file_path}"
        )

    print()

    if result.ai_status != "success":
        print(
            "AI test generation unavailable."
        )

        if result.ai_error:
            print(
                f"Reason: {result.ai_error}"
            )

        return

    generated = result.ai_test_generation

    assert generated is not None

    print(
        "Test strategy:"
    )

    print(
        f"  {generated.test_strategy_summary}"
    )

    print()
    print("Coverage gaps:")

    if generated.coverage_gaps:
        for gap in generated.coverage_gaps:
            print(
                f"  - {gap}"
            )
    else:
        print("  - None identified")

    print()
    print("Generated tests:")

    for index, test in enumerate(
        generated.generated_tests,
        start=1,
    ):
        print()
        print(
            f"{index}. {test.name}"
        )

        print(
            f"   Priority: "
            f"{test.priority.value}"
        )

        print(
            f"   Type: {test.test_type}"
        )

        print(
            f"   Target file: "
            f"{test.target_file}"
        )

        print(
            f"   Purpose: {test.purpose}"
        )

        print()
        print(test.code)

    print()
    print(
        "Confidence: "
        f"{generated.confidence:.2f}"
    )

    if generated.assumptions:
        print()
        print("Assumptions:")

        for assumption in (
            generated.assumptions
        ):
            print(
                f"  - {assumption}"
            )


if __name__ == "__main__":
    main()