from pathlib import Path

from ai_qe.repository.initializer import (
    load_repository_inventory,
)
from ai_qe.repository.test_source import (
    read_test_source,
)


def build_test_context(
    repository_root: Path,
    selected_tests: list[str],
) -> list[dict]:
    inventory = load_repository_inventory(
        repository_root
    )

    tests = inventory.get(
        "tests",
        []
    )

    by_name = {
        test["name"]: test
        for test in tests
    }

    context = []

    for test_name in selected_tests:
        metadata = by_name.get(
            test_name
        )

        if metadata is None:
            continue

        source = read_test_source(
            repository_root=repository_root,
            test_file=metadata[
                "test_file"
            ],
            test_name=test_name,
        )

        context.append(
            {
                "name": test_name,
                "test_file": metadata[
                    "test_file"
                ],
                "test_type": metadata[
                    "test_type"
                ],
                "source": source,
            }
        )

    return context