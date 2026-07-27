from datetime import datetime, timezone

from fastapi.testclient import TestClient


def register_device(
    client: TestClient,
    device_id: str = "sensor-501",
) -> None:
    response = client.post(
        "/devices",
        json={
            "device_id": device_id,
            "name": "Alert Test Sensor",
            "device_type": "temperature_sensor",
        },
    )

    assert response.status_code == 201


def submit_telemetry(
    client: TestClient,
    temperature: float,
    idempotency_key: str,
    device_id: str = "sensor-501",
):
    return client.post(
        "/telemetry",
        json={
            "device_id": device_id,
            "temperature": temperature,
            "pressure": 101.3,
            "recorded_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "idempotency_key": idempotency_key,
        },
    )


def test_temperature_below_threshold_does_not_create_alert(
    client: TestClient,
) -> None:
    register_device(client)

    telemetry_response = submit_telemetry(
        client=client,
        temperature=99.9,
        idempotency_key="below-threshold",
    )

    alert_response = client.get("/alerts")

    assert telemetry_response.status_code == 201
    assert alert_response.status_code == 200
    assert alert_response.json() == []


def test_temperature_at_threshold_creates_alert(
    client: TestClient,
) -> None:
    register_device(client)

    telemetry_response = submit_telemetry(
        client=client,
        temperature=100.0,
        idempotency_key="at-threshold",
    )

    alert_response = client.get("/alerts")

    assert telemetry_response.status_code == 201
    assert alert_response.status_code == 200

    alerts = alert_response.json()

    assert len(alerts) == 1
    assert alerts[0]["device_id"] == "sensor-501"
    assert alerts[0]["alert_type"] == "high_temperature"
    assert alerts[0]["severity"] == "critical"
    assert alerts[0]["measured_value"] == 100.0
    assert alerts[0]["threshold_value"] == 100.0
    assert alerts[0]["acknowledged"] is False
    assert alerts[0]["acknowledged_at"] is None


def test_temperature_above_threshold_creates_alert(
    client: TestClient,
) -> None:
    register_device(client)

    submit_telemetry(
        client=client,
        temperature=100.1,
        idempotency_key="above-threshold",
    )

    response = client.get("/alerts")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["measured_value"] == 100.1


def test_alert_references_telemetry_reading(
    client: TestClient,
) -> None:
    register_device(client)

    telemetry_response = submit_telemetry(
        client=client,
        temperature=120.0,
        idempotency_key="reading-reference",
    )

    alert_response = client.get("/alerts")

    reading_id = telemetry_response.json()["reading_id"]
    alert = alert_response.json()[0]

    assert alert["reading_id"] == reading_id


def test_get_alert_by_id(
    client: TestClient,
) -> None:
    register_device(client)

    submit_telemetry(
        client=client,
        temperature=110.0,
        idempotency_key="get-alert",
    )

    list_response = client.get("/alerts")
    alert_id = list_response.json()[0]["alert_id"]

    response = client.get(
        f"/alerts/{alert_id}"
    )

    assert response.status_code == 200
    assert response.json()["alert_id"] == alert_id


def test_get_unknown_alert_returns_not_found(
    client: TestClient,
) -> None:
    response = client.get(
        "/alerts/unknown-alert"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Alert 'unknown-alert' was not found."
    }


def test_acknowledge_alert(
    client: TestClient,
) -> None:
    register_device(client)

    submit_telemetry(
        client=client,
        temperature=115.0,
        idempotency_key="acknowledge-alert",
    )

    list_response = client.get("/alerts")
    alert_id = list_response.json()[0]["alert_id"]

    response = client.patch(
        f"/alerts/{alert_id}/acknowledge"
    )

    assert response.status_code == 200
    assert response.json()["acknowledged"] is True
    assert response.json()["acknowledged_at"] is not None


def test_acknowledge_alert_is_idempotent(
    client: TestClient,
) -> None:
    register_device(client)

    submit_telemetry(
        client=client,
        temperature=115.0,
        idempotency_key="idempotent-ack",
    )

    list_response = client.get("/alerts")
    alert_id = list_response.json()[0]["alert_id"]

    first_response = client.patch(
        f"/alerts/{alert_id}/acknowledge"
    )

    second_response = client.patch(
        f"/alerts/{alert_id}/acknowledge"
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    assert (
        second_response.json()["acknowledged_at"]
        == first_response.json()["acknowledged_at"]
    )


def test_filter_unacknowledged_alerts(
    client: TestClient,
) -> None:
    register_device(client)

    submit_telemetry(
        client=client,
        temperature=110.0,
        idempotency_key="first-alert",
    )

    submit_telemetry(
        client=client,
        temperature=120.0,
        idempotency_key="second-alert",
    )

    all_alerts = client.get("/alerts").json()

    first_alert_id = all_alerts[0]["alert_id"]

    client.patch(
        f"/alerts/{first_alert_id}/acknowledge"
    )

    response = client.get(
        "/alerts?acknowledged=false"
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["acknowledged"] is False