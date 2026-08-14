from dataclasses import dataclass, field

from ai_qe.datasets import loader as load


PRIORITY_ORDER = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}


@dataclass
class SelectedTest:
    test_id: str
    name: str
    component: str
    test_type: str
    priority: str

    test_file: str | None = None
    execution_time_seconds: float = 0.0
    flaky_score: float = 0.0
    covers: list[str] = field(default_factory=list)
    business_rules: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


def select_tests(
    affected_components: list[str],
) -> list[SelectedTest]:
    inventory = load.load_test_inventory()

    selected: list[SelectedTest] = []

    for test in inventory:
        if test["component"] not in affected_components:
            continue

        selected.append(
            SelectedTest(
                test_id=test["test_id"],
                name=test["name"],
                component=test["component"],
                test_type=test["test_type"],
                priority=test["priority"],

                test_file=test.get("test_file"),

                execution_time_seconds=test.get(
                    "execution_time_seconds",
                    0.0,
                ),

                flaky_score=test.get(
                    "flaky_score",
                    0.0,
                ),

                covers=test.get(
                    "covers",
                    [],
                ),

                business_rules=test.get(
                    "business_rules",
                    [],
                ),

                tags=test.get(
                    "tags",
                    [],
                ),
            )
        )

    selected.sort(
        key=lambda test: (
            -PRIORITY_ORDER.get(
                test.priority,
                0,
            ),
            test.execution_time_seconds,
        )
    )

    return selected