from dataclasses import dataclass

from ai_qe.agents.models import (
    AITestGeneration,
)
from ai_qe.agents.test_generation_agent import (
    TestGenerationAgent,
)
from ai_qe.change_analysis.analyzer import (
    ChangeAnalysisResult,
    analyze_change,
)


@dataclass
class TestGenerationResult:
    analysis: ChangeAnalysisResult
    ai_test_generation: (
        AITestGeneration | None
    )
    ai_status: str
    ai_error: str | None


def generate_tests_for_change(
    base_revision: str,
    target_revision: str,
    agent: TestGenerationAgent,
) -> TestGenerationResult:
    analysis = analyze_change(
        base_revision=base_revision,
        target_revision=target_revision,
    )

    combined_diff = "\n\n".join(
        change.diff
        for change in analysis.changes
    )

    if not combined_diff.strip():
        return TestGenerationResult(
            analysis=analysis,
            ai_test_generation=None,
            ai_status="not_required",
            ai_error=None,
        )

    try:
        generated = agent.generate(
            diff=combined_diff,
            affected_components=(
                analysis.affected_components
            ),
            existing_tests=(
                analysis.selected_tests
            ),
        )

        return TestGenerationResult(
            analysis=analysis,
            ai_test_generation=generated,
            ai_status="success",
            ai_error=None,
        )

    except Exception as exc:
        return TestGenerationResult(
            analysis=analysis,
            ai_test_generation=None,
            ai_status="unavailable",
            ai_error=str(exc),
        )