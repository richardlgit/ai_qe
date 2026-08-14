from dataclasses import dataclass, field


@dataclass
class EvaluationCheck:
    name: str
    passed: bool
    score: float
    category: str = "deterministic"
    details: str = ""


@dataclass
class ScenarioEvaluation:
    scenario_id: str
    checks: list[EvaluationCheck] = field(
        default_factory=list
    )

    def score_for_category(
        self,
        category: str,
        ) -> float:
        checks = [
        check
        for check in self.checks
        if check.category == category
        ]

        if not checks:
            return 0.0

        return sum(
            check.score
            for check in checks
        ) / len(checks)

    @property
    def overall_score(self) -> float:
        if not self.checks:
            return 0.0

        return sum(
            check.score
            for check in self.checks
        ) / len(self.checks)