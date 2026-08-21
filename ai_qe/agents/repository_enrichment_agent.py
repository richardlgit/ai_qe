import json

from ai_qe.agents.models import (
    RepositoryAIEnrichment,
)
from ai_qe.change_analysis.repository_analyzer import (
    RepositoryChangeAnalysis,
)
from ai_qe.llm.base import LLMProvider
from ai_qe.agents.models import (
    RepositoryAIEnrichment,
)

SYSTEM_PROMPT = """
You are a senior Quality Engineering analyst.

Your only objective is to identify test coverage gaps introduced
or exposed by the supplied code change.

Use the Git diff and the actual existing test sources as evidence.

Produce a concise change-coverage plan.

For existing tests affected by the change:
- identify what coverage is missing,
- state exactly what should be changed or strengthened.

For changed behavior with no existing coverage:
- recommend a new behavioral test,
- list the assertions that test must verify.

Important rules:

- Existing tests are evidence of prior expected behavior.
- Do not assume the changed implementation is automatically correct.
- Do not invent test names.
- Do not recommend changing unrelated tests.
- Do not classify tests merely because they belong to the same component.
- Do not repeat unchanged behavior.
- Do not repeat deterministic risk information.
- Do not write a general QE report.
- Keep explanations concise and actionable.
- Recommend behavioral coverage, not implementation-specific test names.
- Every test_name in existing_test_changes MUST exactly match
one of the supplied selected_tests. Never create or rename an
existing test.
- Each entry in new_tests_required should represent one distinct behavior
or failure path.

- Do not combine multiple independent behaviors into one test requirement.

Examples of distinct behaviors include:
- explicit valid UUID handling
- malformed UUID validation
- duplicate creation conflict handling
- unexpected database failure handling
"""


class RepositoryEnrichmentAgent:
    def __init__(
        self,
        provider: LLMProvider,
    ) -> None:
        self.provider = provider

    def analyze(
        self,
        analysis: RepositoryChangeAnalysis,
        test_context: list[dict],
    ) -> RepositoryAIEnrichment:
        combined_diff = "\n\n".join(
            change.diff
            for change in analysis.changes
        )

        context = {
            "affected_components": (
                analysis.affected_components
            ),
            "selected_tests": test_context,
            "deterministic_risk": {
                "score": analysis.risk.score,
                "level": analysis.risk.level,
                "decision": analysis.risk.decision,
                "reasons": analysis.risk.reasons,
            },
        }

        
        user_prompt = f"""
            Analyze the test coverage impact of this repository change.

            Repository evidence:

            {json.dumps(context, indent=2)}

            Git diff:

            {combined_diff}

            Return a concise change-coverage analysis with:

            1. summary
            - no more than 3 sentences

            2. coverage_status
            - use one of:
                "complete"
                "partial"
                "gap"
                "blocked"

            3. existing_test_changes
            - include only existing tests that should be changed or strengthened
            - for each test provide:
                - the specific coverage gap
                - the concrete change needed

            4. new_tests_required
            - include only changed behaviors not adequately covered by existing tests
            - describe the behavior to verify
            - list concrete assertions

            5. unaffected_tests
            - existing selected tests that require no change

            6. remaining_risks
            - only risks that cannot be closed by the recommended tests

            Do not provide long narrative sections.
            Do not invent test names.
            """

        enrichment = self.provider.generate_structured(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        response_model=RepositoryAIEnrichment,
        )

        coverage = enrichment.coverage_analysis

        known_tests = {
            test["name"]
            for test in test_context
        }

        # Keep only real repository tests in
        # existing_test_changes.
        valid_existing_changes = []
        unknown_tests = []

        for item in coverage.existing_test_changes:
            if item.test_name in known_tests:
                valid_existing_changes.append(
                    item
                )
            else:
                unknown_tests.append(
                    item.test_name
                )

        coverage.existing_test_changes = (
            valid_existing_changes
        )

        # A test cannot simultaneously require a
        # change and be classified as unaffected.
        changed_test_names = {
            item.test_name
            for item
            in coverage.existing_test_changes
        }

        coverage.unaffected_tests = [
            test_name
            for test_name
            in coverage.unaffected_tests
            if (
                test_name in known_tests
                and test_name
                not in changed_test_names
            )
        ]

        # Warn rather than fail the whole
        # enrichment response.
        if unknown_tests:
            print(
                "AI warning: ignored unknown "
                "existing tests: "
                + ", ".join(
                    sorted(
                        set(unknown_tests)
                    )
                )
            )


        return enrichment