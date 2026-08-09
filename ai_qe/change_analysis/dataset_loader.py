import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = PROJECT_ROOT / "datasets"


def load_json(filename: str) -> Any:
    path = DATASET_DIR / filename

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)