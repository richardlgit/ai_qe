import json

from ai_qe.agents.models import (
    RepositoryAIAnalysis,
)
from ai_qe.change_analysis.repository_analyzer import (
    RepositoryChangeAnalysis,
)
from ai_qe.llm.base import LLMProvider


SYSTEM_PROMPT = """
You are a senior Quality Engineering analyst.

Analyze a software change using the supplied Git diff,
affected components, selected tests, and deterministic risk result.

Focus on:
- actual behavioral change
- likely failure modes
- missing or weak test coverage
- boundary and negative scenarios
- regression risk

Do not override the deterministic release decision.

Do not invent behavior unsupported by the supplied diff.

Do not recommend tests that validate the changed behavior if that
behavior appears to contradict the intended existing behavior.

Recommend tests primarily for risks directly supported by the supplied
diff and repository context. Do not introduce unrelated validation,
security, or robustness scenarios unless the change directly affects them.

Describe recommended test focus in terms of expected behavior.
For example, prefer "verify alert creation exactly at the critical
threshold" over inventing a test name.

Existing test intent analysis is evidence of prior expected behavior.

When the changed implementation conflicts with an existing test
expectation, treat that as a potential regression unless there is
explicit evidence that the expected behavior intentionally changed.

Do not recommend tests that merely validate the changed implementation
when that implementation conflicts with existing executable expectations.

When test intent evidence and changed code disagree, explicitly describe
the conflict and base QE recommendations on the strongest available
repository evidence.
"""


class RepositoryAnalysisAgent:
    def __init__(
        self,
        provider: LLMProvider,
    ) -> None:
        self.provider = provider

    def analyze(
        self,
        analysis: RepositoryChangeAnalysis,
        test_analysis=None,
        ) -> RepositoryAIAnalysis:

        combined_diff = "\n\n".join(
        change.diff
        for change in analysis.changes
        )
        
        test_intent_context = None

        if test_analysis is not None:
            test_intent_context = {
                "coverage_status": (
                    test_analysis.coverage_status
                ),
                "related_tests": [
                    {
                        "test_name": test.test_name,
                        "classification": (
                            test.classification.value
                        ),
                        "intent": test.intent,
                        "reasoning": test.reasoning,
                    }
                    for test in (
                        test_analysis.related_tests
                    )
                ],
                "coverage_gaps": (
                    test_analysis.coverage_gaps
                ),
                "recommended_tests": (
                    test_analysis.recommended_tests
                ),
                "confidence": (
                    test_analysis.confidence
                ),
            }

        context = {
            "affected_components": (
                analysis.affected_components
            ),
            "selected_tests": (
                analysis.selected_tests
            ),
            "risk": {
                "score": analysis.risk.score,
                "level": analysis.risk.level,
                "decision": (
                    analysis.risk.decision
                ),
                "reasons": (
                    analysis.risk.reasons
                ),
            },
            "test_intent_analysis": (
                test_intent_context
            ),
        }

        user_prompt = f"""
Analyze this repository change from a QE perspective.
The supplied test-intent analysis represents repository-derived evidence
about prior expected behavior.

If it identifies a regression detector, do not recommend changing that
test merely to match the new implementation. Instead, identify the
implementation/test conflict and recommend review of the changed behavior.
Repository context:

{json.dumps(context, indent=2)}

Git diff:

{combined_diff}

Requirements:
- Explain the concrete behavioral change.
- Identify likely failure modes.
- Assess whether the selected tests appear sufficient.
- Recommend additional test focus where needed.
- Provide a QE recommendation consistent with the evidence.
- Confidence must be between 0.0 and 1.0.
- Describe test recommendations as behaviors to verify,
  not invented test function names.
- Do not recommend tests that encode a suspected regression
  as the expected behavior.   
"""

        return self.provider.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=RepositoryAIAnalysis,
        )