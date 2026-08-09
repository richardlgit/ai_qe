from ai_qe.change_analysis.component_mapper import (
    map_files_to_components,
)


def test_alert_service_file_maps_to_component():
    components = map_files_to_components(
        [
            "edgepulse/app/services/"
            "alert_service.py"
        ]
    )

    assert len(components) == 1
    assert components[0].name == "alert_service"