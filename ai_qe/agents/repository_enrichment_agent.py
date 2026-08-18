import json

from ai_qe.agents.models import (
    RepositoryAIEnrichment,
)
from ai_qe.change_analysis.repository_analyzer import (
    RepositoryChangeAnalysis,
)
from ai_qe.llm.base import LLMProvider


SYSTEM_PROMPT = """
You are a senior Quality Engineering analyst.

Analyze a software change together with the actual source of
discovered related tests.

You must perform two connected tasks:

1. Analyze the intent and relevance of the existing tests.
2. Use that test evidence when producing the final QE analysis.

Important principles:

- Existing tests are evidence of prior expected behavior.
- Do not assume the changed implementation is automatically correct.
- If changed code conflicts with an existing test expectation,
  identify the conflict as a potential regression unless there is
  explicit evidence that the expected behavior intentionally changed.
- Do not recommend modifying a valid regression test simply to make
  it agree with the changed implementation.
- Do not invent business requirements.
- Do not classify a test as redundant merely because it does not
  exercise the exact changed condition.
- Redundant means materially equivalent behavior and assertions are
  already covered elsewhere.
- Tests covering neighboring boundary behavior may remain relevant
  even if they do not detect the exact changed case.
- If no related tests exist, treat the changed behavior as a
  coverage gap.
- Recommend test scenarios as behaviors to verify, not invented test names.
- Keep the final QE recommendation consistent with the test-intent analysis.
- The deterministic risk score and release decision are authoritative.
  Do not override or repeat them as your own decision.
For every test supplied in selected_tests, include exactly one entry
in test_analysis.related_tests.

Do not omit a supplied test even if it is unaffected by the change.
Classify unaffected tests as "unaffected".

test_analysis.related_tests may be empty only when selected_tests is empty.
The number of entries in test_analysis.related_tests must equal the
number of tests supplied in selected_tests.
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
            Analyze this repository change.

            Repository evidence:

            {json.dumps(context, indent=2)}

            Git diff:

            {combined_diff}

            Return BOTH:

            A. Test intent analysis
            - infer each related test's behavioral intent from its source,
            - classify its relevance,
            - identify regression detectors,
            - identify unaffected or incomplete coverage,
            - identify redundancy only with strong evidence,
            - identify coverage gaps.

            B. Final QE analysis
            - explain the behavioral change,
            - identify likely failure modes,
            - assess test sufficiency,
            - recommend focused test behavior,
            - reconcile the final recommendation with the test-intent evidence.

            If the changed implementation conflicts with an existing test
            expectation, explicitly call out that conflict.

            Confidence values must be between 0.0 and 1.0.
            """

        enrichment = self.provider.generate_structured(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
                response_model=RepositoryAIEnrichment,
            )

        expected_tests = {
            test["name"]
            for test in test_context
        }

        analyzed_tests = {
            test.test_name
            for test
            in enrichment.test_analysis.related_tests
        }

        missing_tests = (
            expected_tests - analyzed_tests
        )

        if missing_tests:
            raise ValueError(
                "AI test analysis omitted discovered tests: "
                + ", ".join(
                    sorted(missing_tests)
                )
            )

        return enrichment