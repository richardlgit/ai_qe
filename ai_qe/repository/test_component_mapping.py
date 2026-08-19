import ast
from collections import defaultdict
from pathlib import Path

from ai_qe.repository.models import (
    DiscoveredComponent,
    DiscoveredTest,
    DiscoveredFixture,
)

from collections import deque

def _fixture_lookup(
    fixtures: list[DiscoveredFixture],
) -> dict[str, DiscoveredFixture]:
    return {
        fixture.name: fixture
        for fixture in fixtures
    }


def _resolve_fixture_modules(
    fixture_names: set[str],
    fixtures: list[DiscoveredFixture],
) -> set[str]:
    lookup = _fixture_lookup(
        fixtures
    )

    visited: set[str] = set()
    modules: set[str] = set()
    stack = list(fixture_names)

    while stack:
        fixture_name = stack.pop()

        if fixture_name in visited:
            continue

        visited.add(fixture_name)

        fixture = lookup.get(
            fixture_name
        )

        if fixture is None:
            continue

        modules.update(
            fixture.imported_modules
        )

        for dependency in (
            fixture.dependencies
        ):
            if dependency not in visited:
                stack.append(
                    dependency
                )

    return modules

def _test_parameters(
    test_path: Path,
    test_name: str,
) -> set[str]:
    try:
        source = test_path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(
            source,
            filename=str(test_path),
        )

    except (
        UnicodeDecodeError,
        SyntaxError,
    ):
        return set()

    for node in tree.body:
        if (
            isinstance(
                node,
                ast.FunctionDef,
            )
            and node.name == test_name
        ):
            return {
                argument.arg
                for argument
                in node.args.args
            }

    return set()

def _find_conftest_files(
    test_file: Path,
    repository_root: Path,
) -> list[Path]:
    conftest_files: list[Path] = []

    current = test_file.parent

    while True:
        candidate = (
            current / "conftest.py"
        )

        if candidate.exists():
            conftest_files.append(
                candidate
            )

        if current == repository_root:
            break

        if repository_root not in current.parents:
            break

        current = current.parent

    return conftest_files


def _component_lookup(
    components: list[DiscoveredComponent],
) -> dict[str, DiscoveredComponent]:
    return {
        component.name: component
        for component in components
    }


def _transitive_dependencies(
    component_name: str,
    components: list[DiscoveredComponent],
) -> set[str]:
    lookup = _component_lookup(
        components
    )

    visited: set[str] = set()
    queue = deque(
        [component_name]
    )

    while queue:
        current = queue.popleft()

        component = lookup.get(
            current
        )

        if component is None:
            continue

        for dependency in (
            component.dependencies
        ):
            dependency_name = (
                dependency.component
            )

            if (
                dependency_name
                in visited
            ):
                continue

            visited.add(
                dependency_name
            )

            queue.append(
                dependency_name
            )

    visited.discard(
        component_name
    )

    return visited

def _best_component_match(
    module_name: str,
    components: list[DiscoveredComponent],
) -> str | None:
    matches = []

    for component in components:
        if _module_matches_component(
            module_name,
            component,
        ):
            matches.append(
                component.name
            )

    if not matches:
        return None

    return max(
        matches,
        key=lambda name: len(
            name.split(".")
        ),
    )

def _imports_from_file(
    file_path: Path,
) -> set[str]:
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
        return set()

    imports: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(
                    alias.name
                )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            if node.module:
                imports.add(
                    node.module
                )

    return imports


def _module_matches_component(
    module_name: str,
    component: DiscoveredComponent,
) -> bool:
    component_module = component.name

    return (
        module_name == component_module
        or module_name.startswith(
            f"{component_module}."
        )
    )

def _direct_dependencies(
    component_name: str,
    components: list[DiscoveredComponent],
) -> set[str]:
    lookup = _component_lookup(
        components
    )

    component = lookup.get(
        component_name
    )

    if component is None:
        return set()

    return {
        dependency.component
        for dependency
        in component.dependencies
    }


def map_tests_to_components(
    repository_root: Path,
    tests: list[DiscoveredTest],
    components: list[DiscoveredComponent],
    fixtures: list[DiscoveredFixture] | None = None,
) -> dict[str, list[str]]:
    mapping: dict[
        str,
        list[str],
    ] = defaultdict(list)

    if fixtures is None:
        fixtures = []

    mapping: dict[
        str,
        list[str],
    ] = defaultdict(list)


    for test in tests:
        test_path = (
            repository_root
            / test.test_file
        )

        imports = set(
        _imports_from_file(
            test_path
        )
        )

        fixture_names = _test_parameters(
            test_path=test_path,
            test_name=test.name,
        )

        fixture_modules = (
            _resolve_fixture_modules(
                fixture_names=fixture_names,
                fixtures=fixtures,
            )
        
        )

        # print()
        # print("TEST:", test.name)
        # print("fixture_names:", fixture_names)
        # print("fixture_modules:", fixture_modules)
        # print("imports:", imports)

        imports.update(
            fixture_modules
        )

        for conftest_file in _find_conftest_files(
            test_file=test_path,
            repository_root=repository_root,
        ):

            imports.update(
                _imports_from_file(
                    conftest_file
                )
            )

        matched_components: set[str] = set()

        for module_name in imports:
            component_name = (
                _best_component_match(
                    module_name,
                    components,
                )
            )
            # print(
            #     "module:",
            #     module_name,
            #     "-> component:",
            #     component_name,
            # )
            if component_name is None:
                continue

            # Directly imported component
            matched_components.add(
                component_name
            )

            # # Transitively exercised components
            # matched_components.update(
            #     _transitive_dependencies(
            #         component_name,
            #         components,
            #     )
            # )

            matched_components.update(
                _direct_dependencies(
                    component_name,
                    components,
                )
            )


        for component_name in matched_components:
            mapping[
                component_name
            ].append(
                test.name
            )

    return {
        component: sorted(
            set(test_names)
        )
        for component, test_names
        in mapping.items()
    }
