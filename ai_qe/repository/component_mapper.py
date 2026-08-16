from pathlib import Path

from ai_qe.repository.models import (
    DiscoveredComponent,
)


def map_file_to_component(
    file_path: str,
    components: list[DiscoveredComponent],
) -> str | None:
    normalized = Path(file_path).as_posix()

    matches: list[
        tuple[int, str]
    ] = []

    for component in components:
        root = Path(
            component.root_path
        ).as_posix()

        if (
            normalized == root
            or normalized.startswith(
                f"{root}/"
            )
        ):
            matches.append(
                (
                    len(Path(root).parts),
                    component.name,
                )
            )

    if not matches:
        return None

    # Prefer the most specific component.
    matches.sort(
        reverse=True
    )

    return matches[0][1]


def map_files_to_components(
    changed_files: list[str],
    components: list[DiscoveredComponent],
) -> list[str]:
    affected: set[str] = set()

    for file_path in changed_files:
        component = map_file_to_component(
            file_path=file_path,
            components=components,
        )

        if component:
            affected.add(component)

    return sorted(affected)