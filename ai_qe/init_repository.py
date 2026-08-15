import argparse
from pathlib import Path

from ai_qe.repository.initializer import (
    initialize_repository,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Initialize AI-QE for a "
            "Python repository."
        )
    )

    parser.add_argument(
        "repository",
        nargs="?",
        default=".",
        help=(
            "Repository path. "
            "Defaults to current directory."
        ),
    )

    args = parser.parse_args()

    root = Path(args.repository)

    inventory = initialize_repository(
        root
    )

    print()
    print(
        "=== AI-QE Repository Initialization ==="
    )
    print()

    print(
        f"Repository: "
        f"{inventory.repository_name}"
    )

    print(
        "Languages: "
        f"{', '.join(inventory.languages)}"
    )

    print(
        f"Source files: "
        f"{len(inventory.source_files)}"
    )

    print(
        f"Tests discovered: "
        f"{len(inventory.tests)}"
    )

    print(
        f"Components discovered: "
        f"{len(inventory.components)}"
        )


    print()
    print(
        "Configuration written to:"
    )

    print("  .ai-qe/repository.json")
    print("  .ai-qe/components.json")    


if __name__ == "__main__":
    main()