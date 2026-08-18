import json
from dataclasses import asdict
from pathlib import Path

from ai_qe.repository.models import (
    ComponentDependency,
    DiscoveredComponent,
    RepositoryInventory,
)
from ai_qe.repository.scanner import (
    discover_source_files,
)
from ai_qe.repository.test_discovery import (
    discover_tests,
)
from ai_qe.repository.component_discovery import (
    discover_components,
)
from ai_qe.repository.test_component_mapping import (
    map_tests_to_components,
)

def initialize_repository(
    repository_root: Path,
) -> RepositoryInventory:
    repository_root = (
        repository_root.resolve()
    )

    source_files = discover_source_files(
        repository_root
    )

    components = discover_components(
    repository_root=repository_root,
    source_files=source_files,
    )

    tests = discover_tests(
        repository_root
    )

    # 3. Discover components
    components = discover_components(
        repository_root=repository_root,
        source_files=source_files,
    )

     # 4. NEW: Map tests to components
    test_component_map = (
        map_tests_to_components(
            repository_root=repository_root,
            tests=tests,
            components=components,
        )
    )

    languages = sorted(
        {
            source.language
            for source in source_files
        }
    )

     # 6. Build inventory
    inventory = RepositoryInventory(
        repository_name=(
            repository_root.name
        ),
        repository_root=str(
            repository_root
        ),
        languages=languages,
        source_files=source_files,
        tests=tests,
        components=components,
        test_component_map=(
            test_component_map
        ),
    )

    output_directory = (
        repository_root / ".ai-qe"
    )

    output_directory.mkdir(
        exist_ok=True
    )

    output_path = (
        output_directory
        / "repository.json"
    )

    output_path.write_text(
        json.dumps(
            asdict(inventory),
            indent=2,
        ),
        encoding="utf-8",
    )

    components_path = (
        output_directory
        / "components.json"
    )
    
    components_path.write_text(
        json.dumps(
            [
                asdict(component)
                for component
                in components
            ],
            indent=2,
        ),
        encoding="utf-8",
    )

    test_map_path = (
    output_directory
    / "test_component_map.json"
    )

    test_map_path.write_text(
    json.dumps(
        test_component_map,
        indent=2,
    ),
    encoding="utf-8",
)

    return inventory

def load_repository_inventory(
    repository_root: Path,
) -> dict:
    path = (
        repository_root
        / ".ai-qe"
        / "repository.json"
    )

    if not path.exists():
        raise FileNotFoundError(
            "AI-QE repository metadata not found. "
            "Run initialization first."
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

def load_discovered_components(
    repository_root: Path,
) -> list[DiscoveredComponent]:
    path = (
        repository_root
        / ".ai-qe"
        / "components.json"
    )

    if not path.exists():
        raise FileNotFoundError(
            "AI-QE repository metadata not found. "
            "Run 'python -m ai_qe.init_repository .' first."
        )

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    components = []

    for item in data:
        dependencies = [
            ComponentDependency(
                component=dependency[
                    "component"
                ],
                imported_by_files=dependency.get(
                    "imported_by_files",
                    [],
                ),
            )
            for dependency
            in item.get(
                "dependencies",
                [],
            )
        ]

        components.append(
            DiscoveredComponent(
                name=item["name"],
                root_path=item[
                    "root_path"
                ],
                files=item.get(
                    "files",
                    [],
                ),
                dependencies=dependencies,
            )
        )

    return components

