import argparse
import json
from dataclasses import asdict

from ai_qe.change_analysis.analyzer import (
    analyze_change,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze a Git change for "
            "Quality Engineering risk."
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

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON",
    )

    args = parser.parse_args()

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