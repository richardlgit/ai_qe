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
import json
from ai_qe.change_analysis.repository_risk import (
    RepositoryRisk,
    calculate_repository_risk,
)

from ai_qe.agents.models import (
    RepositoryAIAnalysis,
    RepositoryTestAnalysis,
    ChangeCoverageAnalysis,
)

@dataclass
class RepositoryChangeAnalysis:
    base_revision: str
    target_revision: str
    changes: list[GitChange]
    affected_components: list[str]
    selected_tests: list[str]
    risk: RepositoryRisk
    ai_analysis: RepositoryAIAnalysis | None = None
    coverage_analysis: (
    ChangeCoverageAnalysis | None
    ) = None
    ai_status: str = "not_requested"
    ai_error: str | None = None
    # ai_status: str = "not_requested"
    # ai_error: str | None = None
    test_analysis: RepositoryTestAnalysis | None = None
    test_analysis_status: str = "not_requested"
    test_analysis_error: str | None = None


def enrich_repository(
    result: RepositoryChangeAnalysis,
    agent,
    test_context: list[dict],
) -> RepositoryChangeAnalysis:
    try:
        enrichment = agent.analyze(
            analysis=result,
            test_context=test_context,
        )

        result.coverage_analysis = (
            enrichment.coverage_analysis
        )

        result.ai_status = "success"

    except Exception as exc:
        result.ai_status = "unavailable"
        result.ai_error = str(exc)

    return result


def enrich_repository_test_analysis(
    result: RepositoryChangeAnalysis,
    agent,
    test_context: list[dict],
) -> RepositoryChangeAnalysis:
    try:
        result.test_analysis = (
            agent.analyze(
                analysis=result,
                test_context=test_context,
            )
        )

        result.test_analysis_status = (
            "success"
        )

    except Exception as exc:
        result.test_analysis_status = (
            "unavailable"
        )

        result.test_analysis_error = (
            str(exc)
        )

    return result

def analyze_repository_change_with_ai(
    repository_root: Path,
    base_revision: str,
    target_revision: str,
    agent,
    test_analysis=None,
) -> RepositoryChangeAnalysis:
    result = analyze_repository_change(
        repository_root=repository_root,
        base_revision=base_revision,
        target_revision=target_revision,
    )

    try:
        result.ai_analysis = agent.analyze(
        analysis=result,
        test_analysis=test_analysis,
        )
        result.ai_status = "success"

    except Exception as exc:
        result.ai_status = "unavailable"
        result.ai_error = str(exc)

    return result

def enrich_repository_with_ai(
    result: RepositoryChangeAnalysis,
    agent,
    test_analysis=None,
) -> RepositoryChangeAnalysis:
    try:
        result.ai_analysis = agent.analyze(
            analysis=result,
            test_analysis=test_analysis,
        )

        result.ai_status = "success"

    except Exception as exc:
        result.ai_status = "unavailable"
        result.ai_error = str(exc)

    return result

def _load_test_component_map(
    repository_root: Path,
) -> dict[str, list[str]]:
    path = (
        repository_root
        / ".ai-qe"
        / "test_component_map.json"
    )

    if not path.exists():
        raise FileNotFoundError(
            "AI-QE test mapping not found. "
            "Run 'python -m ai_qe.init_repository .' first."
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

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

    test_component_map = (
    _load_test_component_map(
        repository_root
    )
    )

    selected_tests: set[str] = set()

    for component in affected_components:
        selected_tests.update(
            test_component_map.get(
                component,
                [],
            )
        )


    risk = calculate_repository_risk(
        changed_file_count=len(
            changed_files
        ),
        affected_component_count=len(
            affected_components
        ),
        selected_test_count=len(
            selected_tests
        ),
        )

    
    return RepositoryChangeAnalysis(
    base_revision=base_revision,
    target_revision=target_revision,
    changes=changes,
    affected_components=affected_components,
    selected_tests=sorted(
        selected_tests
    ),
    risk=risk,
)