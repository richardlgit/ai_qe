from dataclasses import dataclass

from ai_qe.change_analysis.component_mapper import (
    AffectedComponent,
    map_files_to_components,
)
from ai_qe.change_analysis.defect_matcher import (
    MatchedDefect,
    match_historical_defects,
)
from ai_qe.change_analysis.git_diff import (
    GitChange,
    get_git_changes,
)
from ai_qe.change_analysis.risk_engine import (
    RiskAssessment,
    calculate_risk,
)
from ai_qe.change_analysis.test_selector import (
    SelectedTest,
    select_tests,
)


@dataclass
class ChangeAnalysisResult:
    base_revision: str
    target_revision: str
    changes: list[GitChange]
    affected_components: list[
        AffectedComponent
    ]
    selected_tests: list[SelectedTest]
    historical_defects: list[
        MatchedDefect
    ]
    risk: RiskAssessment


def analyze_change(
    base_revision: str,
    target_revision: str,
) -> ChangeAnalysisResult:
    changes = get_git_changes(
        base_revision=base_revision,
        target_revision=target_revision,
    )

    changed_files = [
        change.file_path
        for change in changes
    ]

    components = map_files_to_components(
        changed_files
    )

    component_names = [
        component.name
        for component in components
    ]

    selected_tests = select_tests(
        affected_components=component_names,
    )

    defects = match_historical_defects(
        affected_components=component_names,
        changed_files=changed_files,
    )

    risk = calculate_risk(
        component_criticalities=[
            component.criticality
            for component in components
        ],
        defect_severities=[
            defect.severity
            for defect in defects
        ],
        escaped_defect_count=sum(
            1
            for defect in defects
            if defect.escaped_to_production
        ),
        selected_test_priorities=[
            test.priority
            for test in selected_tests
        ],
    )

    return ChangeAnalysisResult(
        base_revision=base_revision,
        target_revision=target_revision,
        changes=changes,
        affected_components=components,
        selected_tests=selected_tests,
        historical_defects=defects,
        risk=risk,
    )