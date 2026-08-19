import ast
from pathlib import Path

from ai_qe.repository.models import (
    DiscoveredFixture,
)


def _is_fixture(
    node: ast.FunctionDef,
) -> bool:
    for decorator in node.decorator_list:
        if isinstance(
            decorator,
            ast.Attribute,
        ):
            if (
                isinstance(
                    decorator.value,
                    ast.Name,
                )
                and decorator.value.id == "pytest"
                and decorator.attr == "fixture"
            ):
                return True

        if isinstance(
            decorator,
            ast.Call,
        ):
            func = decorator.func

            if (
                isinstance(
                    func,
                    ast.Attribute,
                )
                and isinstance(
                    func.value,
                    ast.Name,
                )
                and func.value.id == "pytest"
                and func.attr == "fixture"
            ):
                return True

    return False


def _imports_from_tree(
    tree: ast.AST,
) -> list[str]:
    imports: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            if node.module:
                imports.add(node.module)

    return sorted(imports)


def discover_fixtures_in_file(
    file_path: Path,
    repository_root: Path,
) -> list[DiscoveredFixture]:
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

    module_imports = _imports_from_tree(
        tree
    )

    relative_file = str(
        file_path.relative_to(
            repository_root
        )
    )

    fixtures: list[
        DiscoveredFixture
    ] = []

    for node in tree.body:
        if not isinstance(
            node,
            ast.FunctionDef,
        ):
            continue

        if not _is_fixture(node):
            continue

        dependencies = [
            argument.arg
            for argument
            in node.args.args
        ]

        fixtures.append(
            DiscoveredFixture(
                name=node.name,
                source_file=relative_file,
                dependencies=dependencies,
                imported_modules=module_imports,
            )
        )

    return fixtures


def discover_fixtures(
    repository_root: Path,
) -> list[DiscoveredFixture]:
    fixtures: list[
        DiscoveredFixture
    ] = []

    for path in repository_root.rglob(
        "conftest.py"
    ):
        fixtures.extend(
            discover_fixtures_in_file(
                file_path=path,
                repository_root=repository_root,
            )
        )

    return fixtures