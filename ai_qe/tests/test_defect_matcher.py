from ai_qe.change_analysis.defect_matcher import (
    match_historical_defects,
)


def test_alert_change_matches_defect_001():
    defects = match_historical_defects(
        affected_components=[
            "alert_service"
        ],
        changed_files=[
            "edgepulse/app/services/"
            "alert_service.py"
        ],
    )

    defect_ids = {
        defect.defect_id
        for defect in defects
    }

    assert "DEF-001" in defect_ids