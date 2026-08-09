from dataclasses import dataclass

from ai_qe.change_analysis.dataset_loader import (
    load_json,
)


@dataclass
class MatchedDefect:
    defect_id: str
    title: str
    component: str
    severity: str
    defect_type: str
    escaped_to_production: bool


def match_historical_defects(
    affected_components: list[str],
    changed_files: list[str],
) -> list[MatchedDefect]:
    defects = load_json("defects.json")

    matches: list[MatchedDefect] = []

    for defect in defects:
        component_match = (
            defect["component"]
            in affected_components
        )

        file_match = bool(
            set(
                defect.get(
                    "affected_files",
                    [],
                )
            ).intersection(changed_files)
        )

        if not (
            component_match
            or file_match
        ):
            continue

        matches.append(
            MatchedDefect(
                defect_id=defect[
                    "defect_id"
                ],
                title=defect["title"],
                component=defect[
                    "component"
                ],
                severity=defect[
                    "severity"
                ],
                defect_type=defect[
                    "defect_type"
                ],
                escaped_to_production=defect[
                    "escaped_to_production"
                ],
            )
        )

    return matches