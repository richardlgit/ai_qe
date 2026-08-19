import ast
from collections import defaultdict
from pathlib import Path

from ai_qe.repository.models import (
    ComponentDependency,
    DiscoveredComponent,
    SourceFile,
)


IGNORED_COMPONENT_NAMES = {
    "tests",
    "test",
    "docs",
    "scripts",
}

def _component_root_path(
    component_name: str,
) -> str:
    return component_name.replace(
        ".",
        "/",
    )


def test_nested_components_are_discovered(
    tmp_path: Path,
):
    services_dir = (
        tmp_path
        / "sample_app"
        / "services"
    )

    clients_dir = (
        tmp_path
        / "sample_app"
        / "clients"
    )

    services_dir.mkdir(
        parents=True
    )

    clients_dir.mkdir(
        parents=True
    )

    (

    services_dir / "order_service.py"
    ).write_text(
        (
            "from sample_app.clients.payment_client "
            "import PaymentClient\n"
        ),
        encoding="utf-8",
    )

    (

    clients_dir / "payment_client.py"
    ).write_text(
        "class PaymentClient: pass\n",
        encoding="utf-8",
    )

    source_files = [
        SourceFile(
            path=(
                "sample_app/services/"
                "order_service.py"
            ),
            language="python",
            size_bytes=1,
        ),
        SourceFile(
            path=(
                "sample_app/clients/"
                "payment_client.py"
            ),
            language="python",
            size_bytes=1,
        ),
    ]

    components = discover_components(
        repository_root=tmp_path,
        source_files=source_files,
    )

    names = {
        component.name
        for component in components
    }

    assert names == {
        "sample_app.services",
        "sample_app.clients",
    }


def _logical_component(
    file_path: str,
) -> str | None:
    path = Path(file_path)
    parts = path.parts

    if len(parts) < 2:
        return None

    directory_parts = parts[:-1]

    if any(
        part in IGNORED_COMPONENT_NAMES
        for part in directory_parts
    ):
        return None

    # Use up to three directory levels.
    component_parts = directory_parts[:3]

    return ".".join(component_parts)


def _module_to_component(
    module_name: str,
    known_components: set[str],
) -> str | None:
    if not module_name:
        return None

    parts = module_name.split(".")

    # Prefer the most specific known component.
    for length in range(
        len(parts),
        0,
        -1,
    ):
        candidate = ".".join(
            parts[:length]
        )

        if candidate in known_components:
            return candidate

    return None


def _discover_imports(
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


def discover_components(
    repository_root: Path,
    source_files: list[SourceFile],
) -> list[DiscoveredComponent]:
    component_files: dict[
        str,
        list[str],
    ] = defaultdict(list)

    for source_file in source_files:
        component = _logical_component(
            source_file.path
        )

        if component is None:
            continue

        component_files[
            component
        ].append(
            source_file.path
        )

    known_components = set(
        component_files
    )

    dependency_files: dict[
        tuple[str, str],
        list[str],
    ] = defaultdict(list)

    for component, files in (
        component_files.items()
    ):
        for relative_file in files:
            absolute_file = (
                repository_root
                / relative_file
            )

            imported_modules = _discover_imports(
                absolute_file
        )

            for module_name in imported_modules:
                imported_component = (
                    _module_to_component(
                        module_name,
                        known_components,
                    )
                )

                if imported_component is None:
                    continue

                if imported_component == component:
                    continue

                dependency_files[
                    (
                        component,
                        imported_component,
                    )
                ].append(
                    relative_file
                )

    discovered: list[
        DiscoveredComponent
    ] = []

    for component_name in sorted(
        component_files
    ):
        dependencies = []

        for (
            source_component,
            target_component,
        ), files in dependency_files.items():
            if (
                source_component
                != component_name
            ):
                continue

            dependencies.append(
                ComponentDependency(
                    component=(
                        target_component
                    ),
                    imported_by_files=sorted(
                        set(files)
                    ),
                )
            )

        discovered.append(
            DiscoveredComponent(
                name=component_name,
                root_path=_component_root_path(
                    component_name
                ),
                files=sorted(
                    component_files[
                        component_name
                    ]
                ),
                dependencies=sorted(
                    dependencies,
                    key=lambda item: (
                        item.component
                    ),
                ),
            )
        )

    return discovered