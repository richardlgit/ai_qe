from pathlib import Path

from ai_qe.repository.models import (
    DiscoveredComponent,
    DiscoveredTest,
)
from ai_qe.repository.test_component_mapping import (
    map_tests_to_components,
)
from ai_qe.repository.models import (
    ComponentDependency,
)

def test_test_import_maps_to_component(
    tmp_path: Path,
):
    test_dir = (
        tmp_path / "tests"
    )
    test_dir.mkdir()

    test_file = (
        test_dir / "test_orders.py"
    )

    test_file.write_text(
        (
            "from sample_app.services."
            "order_service import OrderService\n"
            "\n"
            "def test_order():\n"
            "    assert True\n"
        ),
        encoding="utf-8",
    )

    components = [
        DiscoveredComponent(
            name="sample_app.services",
            root_path=(
                "sample_app/services"
            ),
        )
    ]

    tests = [
        DiscoveredTest(
            name="test_order",
            test_file=(
                "tests/test_orders.py"
            ),
            test_type="function",
        )
    ]

    mapping = map_tests_to_components(
        repository_root=tmp_path,
        tests=tests,
        components=components,
    )

    assert mapping == {
        "sample_app.services": [
            "test_order"
        ]
    }

def test_unrelated_import_does_not_map(
    tmp_path: Path,
):
    test_dir = (
        tmp_path / "tests"
    )
    test_dir.mkdir()

    test_file = (
        test_dir / "test_math.py"
    )

    test_file.write_text(
        (
            "import math\n"
            "\n"
            "def test_math():\n"
            "    assert math.sqrt(4) == 2\n"
        ),
        encoding="utf-8",
    )

    components = [
        DiscoveredComponent(
            name="sample_app.services",
            root_path=(
                "sample_app/services"
            ),
        )
    ]

    tests = [
        DiscoveredTest(
            name="test_math",
            test_file=(
                "tests/test_math.py"
            ),
            test_type="function",
        )
    ]

    mapping = map_tests_to_components(
        repository_root=tmp_path,
        tests=tests,
        components=components,
    )

    assert mapping == {}

def test_test_maps_to_transitive_component_dependency(
    tmp_path: Path,
):
    test_dir = (
        tmp_path / "tests"
    )

    test_dir.mkdir()

    test_file = (
        test_dir / "test_orders.py"
    )

    test_file.write_text(
        (
            "from sample_app.api.orders "
            "import create_order\n"
            "\n"
            "def test_create_order():\n"
            "    assert True\n"
        ),
        encoding="utf-8",
    )

    components = [
        DiscoveredComponent(
            name="sample_app.api",
            root_path="sample_app/api",
            dependencies=[
                ComponentDependency(
                    component=(
                        "sample_app.services"
                    ),
                    imported_by_files=[
                        "sample_app/api/orders.py"
                    ],
                )
            ],
        ),
        DiscoveredComponent(
            name="sample_app.services",
            root_path=(
                "sample_app/services"
            ),
        ),
    ]

    tests = [
        DiscoveredTest(
            name="test_create_order",
            test_file=(
                "tests/test_orders.py"
            ),
            test_type="function",
        )
    ]

    mapping = map_tests_to_components(
        repository_root=tmp_path,
        tests=tests,
        components=components,
    )

    assert (
        mapping[
            "sample_app.api"
        ]
        == ["test_create_order"]
    )

    assert (
        mapping[
            "sample_app.services"
        ]
        == ["test_create_order"]
    )

def test_dependency_mapping_handles_cycles(
    tmp_path: Path,
):
    test_dir = (
        tmp_path / "tests"
    )

    test_dir.mkdir()

    test_file = (
        test_dir / "test_cycle.py"
    )

    test_file.write_text(
        (
            "from sample_app.api "
            "import handler\n"
            "\n"
            "def test_cycle():\n"
            "    assert True\n"
        ),
        encoding="utf-8",
    )

    components = [
        DiscoveredComponent(
            name="sample_app.api",
            root_path="sample_app/api",
            dependencies=[
                ComponentDependency(
                    component=(
                        "sample_app.services"
                    )
                )
            ],
        ),
        DiscoveredComponent(
            name="sample_app.services",
            root_path=(
                "sample_app/services"
            ),
            dependencies=[
                ComponentDependency(
                    component=(
                        "sample_app.api"
                    )
                )
            ],
        ),
    ]

    tests = [
        DiscoveredTest(
            name="test_cycle",
            test_file=(
                "tests/test_cycle.py"
            ),
            test_type="function",
        )
    ]

    mapping = map_tests_to_components(
        repository_root=tmp_path,
        tests=tests,
        components=components,
    )

    assert "sample_app.api" in mapping
    assert "sample_app.services" in mapping