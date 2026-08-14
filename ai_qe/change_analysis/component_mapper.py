from dataclasses import dataclass
from ai_qe.datasets import loader as load

from ai_qe.change_analysis.dataset_loader import (
    load_json,
)


@dataclass
class AffectedComponent:
    component_id: str
    name: str
    criticality: str
    business_impact: str
    matched_files: list[str]


def map_files_to_components(
    changed_files: list[str],
) -> list[AffectedComponent]:
    components = load.load_component_map()

    affected: list[AffectedComponent] = []

    for component in components:
        component_files = set(
            component.get("files", [])
        )

        matched_files = [
            file_path
            for file_path in changed_files
            if file_path in component_files
        ]

        if matched_files:
            affected.append(
                AffectedComponent(
                    component_id=component[
                        "component_id"
                    ],
                    name=component["name"],
                    criticality=component[
                        "criticality"
                    ],
                    business_impact=component[
                        "business_impact"
                    ],
                    matched_files=matched_files,
                )
            )

    return affected