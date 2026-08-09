import json
import os

from openai import OpenAI

from ai_qe.agents.models import AIChangeAnalysis
from ai_qe.change_analysis.component_mapper import (
    AffectedComponent,
)
from openai import (
    OpenAI,
    APIError,
    RateLimitError,
    APITimeoutError,
)


SYSTEM_PROMPT = """
You are a senior Quality Engineering change-risk analyst.

Analyze software code changes from a Quality Engineering perspective.

Focus on:
- behavioral changes
- boundary conditions
- failure modes
- regression risks
- security implications
- reliability implications
- data integrity
- missing validation
- concurrency or retry behavior
- backward compatibility

Do not decide whether a release should ship.

Do not invent facts that are not supported by the supplied code diff
or component context.

Clearly distinguish likely risks from confirmed defects.
"""


class ChangeAnalysisAgent:
    def __init__(
        self,
        model: str | None = None,
    ) -> None:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError(
                "OPENAI_API_KEY is not configured."
            )

        self.client = OpenAI()

        self.model = (
            model
            or os.getenv("AI_QE_MODEL")
            or "gpt-5-nano"
        )

    def analyze(
        self,
        diff: str,
        affected_components: list[AffectedComponent],
    ) -> AIChangeAnalysis:
        component_context = [
            {
                "name": component.name,
                "criticality": component.criticality,
                "business_impact": component.business_impact,
                "matched_files": component.matched_files,
            }
            for component in affected_components
        ]

        user_prompt = f"""
Analyze this software change.

Affected component context:

{json.dumps(component_context, indent=2)}

Git diff:

{diff}

Return a Quality Engineering analysis.

Pay particular attention to changes in comparison operators,
conditional logic, validation logic, retry behavior, authentication,
error handling, persistence, and boundary conditions.
"""
        try:
            response = self.client.responses.parse(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            text_format=AIChangeAnalysis,
        )

            return response.output_parsed
        except (
            RateLimitError,
            APITimeoutError,
            APIError,
        ):
            raise