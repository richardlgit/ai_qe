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