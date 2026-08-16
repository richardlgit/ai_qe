import argparse
from pathlib import Path

from ai_qe.change_analysis.repository_analyzer import (
    analyze_repository_change,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze a Git change using "
            "AI-QE discovered repository metadata."
        )
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


if __name__ == "__main__":
    main()