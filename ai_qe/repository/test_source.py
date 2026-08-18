import ast
from pathlib import Path


def read_test_source(
    repository_root: Path,
    test_file: str,
    test_name: str,
) -> str | None:
    path = (
        repository_root
        / test_file
    )

    if not path.exists():
        return None

    try:
        source = path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(
            source,
            filename=str(path),
        )

    except (
        UnicodeDecodeError,
        SyntaxError,
    ):
        return None

    for node in tree.body:
        if (
            isinstance(
                node,
                ast.FunctionDef,
            )
            and node.name == test_name
        ):
            return ast.get_source_segment(
                source,
                node,
            )

        if isinstance(
            node,
            ast.ClassDef,
        ):
            for child in node.body:
                qualified_name = (
                    f"{node.name}::{child.name}"
                    if isinstance(
                        child,
                        ast.FunctionDef,
                    )
                    else None
                )

                if (
                    qualified_name
                    == test_name
                ):
                    return ast.get_source_segment(
                        source,
                        child,
                    )

    return None