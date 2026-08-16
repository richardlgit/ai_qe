from dataclasses import dataclass
from pathlib import Path

from ai_qe.change_analysis.git_diff import (
    GitChange,
    get_git_changes,
)
from ai_qe.repository.component_mapper import (
    map_files_to_components,
)
from ai_qe.repository.initializer import (
    load_discovered_components,
)


@dataclass
class RepositoryChangeAnalysis:
    base_revision: str
    target_revision: str
    changes: list[GitChange]
    affected_components: list[str]


def analyze_repository_change(
    repository_root: Path,
    base_revision: str,
    target_revision: str,
) -> RepositoryChangeAnalysis:
    repository_root = repository_root.resolve()

    components = load_discovered_components(
        repository_root
    )

    changes = get_git_changes(
        base_revision=base_revision,
        target_revision=target_revision,
    )

    changed_files = [
        change.file_path
        for change in changes
    ]

    affected_components = (
        map_files_to_components(
            changed_files=changed_files,
            components=components,
        )
    )

    return RepositoryChangeAnalysis(
        base_revision=base_revision,
        target_revision=target_revision,
        changes=changes,
        affected_components=affected_components,
    )