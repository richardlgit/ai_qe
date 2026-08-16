import ast
from collections import defaultdict
from pathlib import Path

from ai_qe.repository.models import (
    DiscoveredComponent,
    DiscoveredTest,
)

from collections import deque


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
) -> dict[str, list[str]]:
    mapping: dict[
        str,
        list[str],
    ] = defaultdict(list)

    for test in tests:
        test_path = (
            repository_root
            / test.test_file
        )

        imports = _imports_from_file(
            test_path
        )

        matched_components: set[str] = set()

        for module_name in imports:
            component_name = (
                _best_component_match(
                    module_name,
                    components,
                )
            )

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


        for component_name in (
            matched_components
        ):
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
