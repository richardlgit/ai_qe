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
from ai_qe.agents.models import AIChangeAnalysis
from dataclasses import dataclass, field
from enum import Enum

class AIStatus(str, Enum):
    NOT_REQUESTED = "not_requested"
    SUCCESS = "success"
    UNAVAILABLE = "unavailable"

@dataclass
class ChangeAnalysisResult:
    base_revision: str
    target_revision: str
    changes: list[GitChange]
    affected_components: list[AffectedComponent]
    selected_tests: list[SelectedTest]
    historical_defects: list[MatchedDefect]
    risk: RiskAssessment

    ai_analysis: AIChangeAnalysis | None = None
    ai_status: str = "not_requested"
    ai_error: str | None = None


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


def analyze_change_with_ai(
    base_revision: str,
    target_revision: str,
    agent,
) -> ChangeAnalysisResult:
    result = analyze_change(
        base_revision=base_revision,
        target_revision=target_revision,
    )

    combined_diff = "\n\n".join(
        change.diff
        for change in result.changes
    )

    if not combined_diff.strip():
        return result

    try:
        ai_analysis = agent.analyze(
            diff=combined_diff,
            affected_components=result.affected_components,
        )

        result.ai_analysis = ai_analysis
        result.ai_status = AIStatus.SUCCESS

    except Exception as exc:
        result.ai_status = AIStatus.UNAVAILABLE
        result.ai_error = str(exc)

        print()
        print("AI enrichment unavailable.")
        print(f"Reason: {exc}")
        print("Continuing with deterministic analysis.")    

    return result

    