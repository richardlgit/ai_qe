from pathlib import Path

from ai_qe.repository.component_mapper import (
    map_files_to_components,
)
from ai_qe.repository.models import (
    DiscoveredComponent,
)


def test_changed_service_file_maps_to_discovered_component():
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
            )
        ],
        components=components,
    )

    assert result == [
        "sample_app.services"
    ]