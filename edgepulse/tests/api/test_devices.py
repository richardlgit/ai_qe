from fastapi.testclient import TestClient


def test_register_device(
    client: TestClient,
) -> None:
    response = client.post(
        "/devices",
        json={
            "device_id": "sensor-104",
            "name": "Boiler Room Sensor",
            "device_type": "temperature_sensor",
        },
    )

    assert response.status_code == 201

    response_body = response.json()

    assert response_body["device_id"] == "sensor-104"
    assert response_body["name"] == "Boiler Room Sensor"
    assert response_body["device_type"] == "temperature_sensor"
    assert response_body["status"] == "active"
    assert response_body["registered_at"] is not None
    assert response_body["last_seen_at"] is None


def test_register_duplicate_device_returns_conflict(
    client: TestClient,
) -> None:
    request_body = {
        "device_id": "sensor-104",
        "name": "Boiler Room Sensor",
        "device_type": "temperature_sensor",
    }

    first_response = client.post(
        "/devices",
        json=request_body,
    )

    second_response = client.post(
        "/devices",
        json=request_body,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409

    assert second_response.json() == {
        "detail": "Device 'sensor-104' already exists."
    }


def test_get_registered_device(
    client: TestClient,
) -> None:
    client.post(
        "/devices",
        json={
            "device_id": "sensor-104",
            "name": "Boiler Room Sensor",
            "device_type": "temperature_sensor",
        },
    )

    response = client.get("/devices/sensor-104")

    assert response.status_code == 200
    assert response.json()["device_id"] == "sensor-104"


def test_get_unknown_device_returns_not_found(
    client: TestClient,
) -> None:
    response = client.get("/devices/missing-sensor")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Device 'missing-sensor' was not found."
    }


def test_list_devices(
    client: TestClient,
) -> None:
    client.post(
        "/devices",
        json={
            "device_id": "sensor-104",
            "name": "Temperature Sensor",
            "device_type": "temperature_sensor",
        },
    )

    client.post(
        "/devices",
        json={
            "device_id": "sensor-105",
            "name": "Pressure Sensor",
            "device_type": "pressure_sensor",
        },
    )

    response = client.get("/devices")

    assert response.status_code == 200

    devices = response.json()

    assert len(devices) == 2

    returned_ids = {
        device["device_id"]
        for device in devices
    }

    assert returned_ids == {
        "sensor-104",
        "sensor-105",
    }


def test_reject_invalid_device_identifier(
    client: TestClient,
) -> None:
    response = client.post(
        "/devices",
        json={
            "device_id": "sensor 104!",
            "name": "Invalid Sensor",
            "device_type": "temperature_sensor",
        },
    )

    assert response.status_code == 422

def test_deactivate_device(
    client: TestClient,
) -> None:
    client.post(
        "/devices",
        json={
            "device_id": "sensor-201",
            "name": "Factory Floor Sensor",
            "device_type": "temperature_sensor",
        },
    )

    response = client.patch(
        "/devices/sensor-201/status",
        json={
            "status": "inactive",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "inactive"


def test_reactivate_device(
    client: TestClient,
) -> None:
    client.post(
        "/devices",
        json={
            "device_id": "sensor-201",
            "name": "Factory Floor Sensor",
            "device_type": "temperature_sensor",
        },
    )

    client.patch(
        "/devices/sensor-201/status",
        json={
            "status": "inactive",
        },
    )

    response = client.patch(
        "/devices/sensor-201/status",
        json={
            "status": "active",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "active"


def test_update_unknown_device_status_returns_not_found(
    client: TestClient,
) -> None:
    response = client.patch(
        "/devices/unknown-device/status",
        json={
            "status": "inactive",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Device 'unknown-device' was not found."
    }


def test_reject_invalid_device_status(
    client: TestClient,
) -> None:
    client.post(
        "/devices",
        json={
            "device_id": "sensor-201",
            "name": "Factory Floor Sensor",
            "device_type": "temperature_sensor",
        },
    )

    response = client.patch(
        "/devices/sensor-201/status",
        json={
            "status": "retired",
        },
    )

    assert response.status_code == 422


def test_status_change_is_persisted(
    client: TestClient,
) -> None:
    client.post(
        "/devices",
        json={
            "device_id": "sensor-201",
            "name": "Factory Floor Sensor",
            "device_type": "temperature_sensor",
        },
    )

    update_response = client.patch(
        "/devices/sensor-201/status",
        json={
            "status": "inactive",
        },
    )

    get_response = client.get(
        "/devices/sensor-201"
    )

    assert update_response.status_code == 200
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "inactive"