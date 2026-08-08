from datetime import datetime, timezone

from fastapi.testclient import TestClient


def create_device(
    client: TestClient,
    device_id: str,
) -> None:
    response = client.post(
        "/devices",
        json={
            "device_id": device_id,
            "name": "Authenticated Device",
            "device_type": "temperature_sensor",
        },
    )

    assert response.status_code == 201


def payload(
    device_id: str,
    key: str,
) -> dict[str, object]:
    return {
        "device_id": device_id,
        "temperature": 72.0,
        "pressure": 101.3,
        "recorded_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "idempotency_key": key,
    }


def test_issue_device_token(
    client: TestClient,
) -> None:
    create_device(
        client,
        "sensor-auth-1",
    )

    response = client.post(
        "/devices/sensor-auth-1/token"
    )

    assert response.status_code == 200
    assert response.json()["device_id"] == "sensor-auth-1"
    assert response.json()["token"]
    assert response.json()["token_type"] == "bearer"


def test_issue_token_for_unknown_device(
    client: TestClient,
) -> None:
    response = client.post(
        "/devices/unknown-device/token"
    )

    assert response.status_code == 404


def test_missing_token_is_rejected(
    client: TestClient,
) -> None:
    create_device(
        client,
        "sensor-auth-2",
    )

    response = client.post(
        "/telemetry",
        json=payload(
            "sensor-auth-2",
            "missing-token",
        ),
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "A device bearer token is required."
    }


def test_invalid_token_is_rejected(
    client: TestClient,
) -> None:
    create_device(
        client,
        "sensor-auth-3",
    )

    response = client.post(
        "/telemetry",
        json=payload(
            "sensor-auth-3",
            "invalid-token",
        ),
        headers={
            "Authorization": "Bearer invalid-token"
        },
    )

    assert response.status_code == 401


def test_valid_token_allows_telemetry(
    client: TestClient,
) -> None:
    create_device(
        client,
        "sensor-auth-4",
    )

    token_response = client.post(
        "/devices/sensor-auth-4/token"
    )

    token = token_response.json()["token"]

    response = client.post(
        "/telemetry",
        json=payload(
            "sensor-auth-4",
            "valid-token",
        ),
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 201


def test_token_cannot_authenticate_other_device(
    client: TestClient,
) -> None:
    create_device(
        client,
        "sensor-auth-5",
    )

    create_device(
        client,
        "sensor-auth-6",
    )

    token_response = client.post(
        "/devices/sensor-auth-5/token"
    )

    token = token_response.json()["token"]

    response = client.post(
        "/telemetry",
        json=payload(
            "sensor-auth-6",
            "wrong-device-token",
        ),
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 401


def test_new_token_revokes_old_token(
    client: TestClient,
) -> None:
    create_device(
        client,
        "sensor-auth-7",
    )

    first_token_response = client.post(
        "/devices/sensor-auth-7/token"
    )

    old_token = first_token_response.json()["token"]

    second_token_response = client.post(
        "/devices/sensor-auth-7/token"
    )

    new_token = second_token_response.json()["token"]

    old_response = client.post(
        "/telemetry",
        json=payload(
            "sensor-auth-7",
            "old-token",
        ),
        headers={
            "Authorization": f"Bearer {old_token}"
        },
    )

    new_response = client.post(
        "/telemetry",
        json=payload(
            "sensor-auth-7",
            "new-token",
        ),
        headers={
            "Authorization": f"Bearer {new_token}"
        },
    )

    assert old_response.status_code == 401
    assert new_response.status_code == 201