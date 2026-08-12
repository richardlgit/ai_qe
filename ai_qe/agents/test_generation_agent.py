import json

from ai_qe.agents.models import (
    AITestGeneration,
)
from ai_qe.change_analysis.component_mapper import (
    AffectedComponent,
)
from ai_qe.change_analysis.test_selector import (
    SelectedTest,
)
from ai_qe.llm.base import LLMProvider


SYSTEM_PROMPT = """
You are a senior Software Quality Engineer.

Your task is to propose high-value automated pytest tests
for a software change.

Focus on:
- changed behavior
- boundary conditions
- regression risk
- negative testing
- validation
- error paths
- security implications
- data integrity
- retry and idempotency behavior

Do not rewrite the production code.

Do not assume APIs or functions that are not supported by
the supplied context.

Prefer small, focused tests over large end-to-end tests.

Generated tests must be suitable for human review before
being added to the repository.
"""


class TestGenerationAgent:
    def __init__(
        self,
        provider: LLMProvider,
    ) -> None:
        self.provider = provider

    def generate(
        self,
        diff: str,
        affected_components: list[
            AffectedComponent
        ],
        existing_tests: list[
            SelectedTest
        ],
    ) -> AITestGeneration:
        component_context = [
            {
                "name": component.name,
                "criticality": component.criticality,
                "business_impact": (
                    component.business_impact
                ),
                "matched_files": (
                    component.matched_files
                ),
            }
            for component
            in affected_components
        ]

        test_context = [
            {
                "test_id": test.test_id,
                "name": test.name,
                "component": test.component,
                "test_type": test.test_type,
                "priority": test.priority,
            }
            for test in existing_tests
        ]

        user_prompt = f"""
Generate pytest test suggestions for this software change.

Affected components:

{json.dumps(component_context, indent=2)}

Existing relevant tests:

{json.dumps(test_context, indent=2)}

Git diff:

{diff}

Requirements:

1. Identify any missing test coverage.
2. Generate focused pytest tests for the changed behavior.
3. Avoid duplicating existing tests unless the existing test
   should be strengthened.
4. Include exact test code.
5. Specify the intended target test file.
6. Explain the purpose of each test.
7. Prefer boundary and negative cases where appropriate.
8. Confidence must be between 0.0 and 1.0.

Do not modify production code.
"""

        return self.provider.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=AITestGeneration,
        )