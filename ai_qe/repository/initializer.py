import json
from dataclasses import asdict
from pathlib import Path

from ai_qe.repository.models import (
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

    languages = sorted(
        {
            source.language
            for source in source_files
        }
    )

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

    return inventory