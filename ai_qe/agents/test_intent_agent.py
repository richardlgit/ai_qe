import json

from ai_qe.agents.models import (
    RepositoryTestAnalysis,
)
from ai_qe.change_analysis.repository_analyzer import (
    RepositoryChangeAnalysis,
)
from ai_qe.llm.base import LLMProvider


SYSTEM_PROMPT = """
You are a senior Quality Engineering analyst.

Analyze a software change together with its discovered tests.

Your job is to determine:

- whether existing tests remain relevant,
- whether they detect a regression,
- whether the change introduces an uncovered behavior,
- whether tests appear redundant,
- and what additional test scenarios may be needed.

Important rules:

- Existing tests are evidence of prior expected behavior.
- Do not assume changed implementation behavior is automatically correct.
- Do not label a test obsolete unless the supplied evidence strongly
  suggests the underlying requirement intentionally changed.
- Do not invent business requirements.
- If there are no related tests, treat that as a coverage gap.
- Recommend tests in terms of behavior to verify, not invented function names.
"""


class TestIntentAgent:
    def __init__(
        self,
        provider: LLMProvider,
    ) -> None:
        self.provider = provider

    def analyze(
        self,
        analysis: RepositoryChangeAnalysis,
        test_context: list[dict],
    ) -> RepositoryTestAnalysis:
        combined_diff = "\n\n".join(
            change.diff
            for change in analysis.changes
        )

        context = {
            "affected_components": (
                analysis.affected_components
            ),
            "selected_tests": test_context,
        }

        user_prompt = f"""
Analyze test relevance for this change.

Repository context:

{json.dumps(context, indent=2)}

Git diff:

{combined_diff}

If related tests exist:
- infer each test's intent from its source,
- determine whether it is still relevant,
- identify possible regression detectors,
- identify possible obsolete expectations,
- identify genuine redundancy only when evidence is strong.

If no related tests exist:
- set coverage_status to "gap",
- explain the uncovered changed behavior,
- recommend focused tests for the changed behavior.

Use only the supplied repository evidence.
"""

        return self.provider.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=RepositoryTestAnalysis,
        )