from ai_qe.change_analysis.test_selector import (
    select_tests,
)


def test_alert_service_selects_critical_tests():
    tests = select_tests(
        ["alert_service"]
    )

    test_ids = {
        test.test_id
        for test in tests
    }

    assert "TEST-002" in test_ids
    assert "TEST-004" in test_ids