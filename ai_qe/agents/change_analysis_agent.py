import json

from ai_qe.agents.models import AIChangeAnalysis
from ai_qe.change_analysis.component_mapper import (
    AffectedComponent,
)
from ai_qe.llm.base import LLMProvider


SYSTEM_PROMPT = """
You are a senior Quality Engineering change-risk analyst.

Analyze software changes from a Quality Engineering perspective.

Focus on:
- behavioral changes
- boundary conditions
- failure modes
- regression risks
- security implications
- reliability implications
- data integrity
- missing validation
- concurrency and retry behavior
- backward compatibility

Do not decide whether a release should ship.

Do not invent facts unsupported by the supplied code diff
or component context.

Clearly distinguish likely risks from confirmed defects.
Confidence must be a decimal between 0.0 and 1.0.
For example, use 0.95, not 95.
"""


class ChangeAnalysisAgent:
    def __init__(
        self,
        provider: LLMProvider,
    ) -> None:
        self.provider = provider

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

Identify:
- the behavioral change
- likely failure modes
- regression risks
- relevant test-focus areas
- your confidence in the analysis

Base your conclusions only on the supplied diff and
component context.
"""

        return self.provider.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=AIChangeAnalysis,
        )