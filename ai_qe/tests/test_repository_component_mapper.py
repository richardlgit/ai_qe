from ai_qe.repository.component_mapper import (
    map_file_to_component,
    map_files_to_components,
)
from ai_qe.repository.models import (
    DiscoveredComponent,
)


def test_file_maps_to_most_specific_component():
    components = [
        DiscoveredComponent(
            name="sample_app",
            root_path="sample_app",
        ),
        DiscoveredComponent(
            name="sample_app.services",
            root_path="sample_app/services",
        ),
    ]

    result = map_file_to_component(
        file_path=(
            "sample_app/services/"
            "order_service.py"
        ),
        components=components,
    )

    assert result == (
        "sample_app.services"
    )


def test_multiple_changed_files_map_to_components():
    components = [
        DiscoveredComponent(
            name="sample_app.services",
            root_path="sample_app/services",
        ),
        DiscoveredComponent(
            name="sample_app.api",
            root_path="sample_app/api",
        ),
    ]

    result = map_files_to_components(
        changed_files=[
            (
                "sample_app/services/"
                "order_service.py"
            ),
            "sample_app/api/orders.py",
        ],
        components=components,
    )

    assert result == [
        "sample_app.api",
        "sample_app.services",
    ]


def test_unknown_file_returns_none():
    components = [
        DiscoveredComponent(
            name="sample_app.services",
            root_path="sample_app/services",
        )
    ]

    result = map_file_to_component(
        file_path="docs/readme.md",
        components=components,
    )

    assert result is None