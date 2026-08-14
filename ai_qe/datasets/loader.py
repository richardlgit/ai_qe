from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path


DATASET_DIR = Path(__file__).parent


@lru_cache(maxsize=None)
def load_json(filename: str):
    path = DATASET_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    with path.open(
        encoding="utf-8"
    ) as file:
        return json.load(file)


@lru_cache(maxsize=None)
def load_component_map():
    return load_json("components.json")


@lru_cache(maxsize=None)
def load_historical_defects():
    return load_json("defects.json")


@lru_cache(maxsize=None)
def load_test_inventory():
    return load_json("test_inventory.json")


@lru_cache(maxsize=None)
def load_changed_scenario(
    scenario_id: str,
):
    scenario_files = {
        "SCN-001": "SCN-001-alert-boundary.json",
    }

    filename = scenario_files.get(scenario_id)

    if filename is None:
        raise ValueError(
            f"Unknown scenario: {scenario_id}"
        )

    return load_json(
        f"changed_scenarios/{filename}"
    )


@lru_cache(maxsize=None)
def load_changed_scenario_expected(
    scenario_id: str,
):
    return load_json(
        f"changed_scenarios/"
        f"{scenario_id}-expected.json"
    )