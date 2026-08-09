from dataclasses import dataclass

from ai_qe.change_analysis.dataset_loader import (
    load_json,
)


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
    execution_time_seconds: float
    flaky_score: float


def select_tests(
    affected_components: list[str],
) -> list[SelectedTest]:
    inventory = load_json(
        "test_inventory.json"
    )

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
                execution_time_seconds=test[
                    "execution_time_seconds"
                ],
                flaky_score=test[
                    "flaky_score"
                ],
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