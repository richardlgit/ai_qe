import ast
from pathlib import Path

from ai_qe.repository.models import (
    DiscoveredTest,
)

from ai_qe.repository.scanner import should_ignore


def is_test_file(
    path: Path,
) -> bool:
    return (
        path.name.startswith("test_")
        or path.name.endswith("_test.py")
    )


def discover_tests_in_file(
    file_path: Path,
    repository_root: Path,
) -> list[DiscoveredTest]:
    try:
        source = file_path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(
            source,
            filename=str(file_path),
        )

    except (
        UnicodeDecodeError,
        SyntaxError,
    ):
        return []

    tests: list[DiscoveredTest] = []

    relative_path = str(
        file_path.relative_to(
            repository_root
        )
    )

    for node in tree.body:
        if (
            isinstance(
                node,
                ast.FunctionDef,
            )
            and node.name.startswith(
                "test_"
            )
        ):
            tests.append(
                DiscoveredTest(
                    name=node.name,
                    test_file=relative_path,
                    test_type="function",
                )
            )

        if isinstance(
            node,
            ast.ClassDef,
        ):
            for child in node.body:
                if (
                    isinstance(
                        child,
                        ast.FunctionDef,
                    )
                    and child.name.startswith(
                        "test_"
                    )
                ):
                    tests.append(
                        DiscoveredTest(
                            name=(
                                f"{node.name}::"
                                f"{child.name}"
                            ),
                            test_file=relative_path,
                            test_type="method",
                        )
                    )

    return tests


def discover_tests(
    repository_root: Path,
) -> list[DiscoveredTest]:
    tests: list[DiscoveredTest] = []

    for path in repository_root.rglob("*.py"):
        relative_path = path.relative_to(
            repository_root
        )

        if should_ignore(relative_path):
            continue

        if not is_test_file(path):
            continue

        tests.extend(
            discover_tests_in_file(
                file_path=path,
                repository_root=repository_root,
            )
        )

    return sorted(
        tests,
        key=lambda item: (
            item.test_file,
            item.name,
        ),
    )