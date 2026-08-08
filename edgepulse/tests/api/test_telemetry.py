from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient


# def register_device(
#     client: TestClient,
#     device_id: str = "sensor-401",
# ) -> None:
#     response = client.post(
#         "/devices",
#         json={
#             "device_id": device_id,
#             "name": "Test Sensor",
#             "device_type": "temperature_sensor",
#         },
#     )

#     assert response.status_code == 201

def authorization_headers(
    token: str,
) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}"
    }


def register_device(
    client: TestClient,
    device_id: str = "sensor-401",
) -> str:
    response = client.post(
        "/devices",
        json={
            "device_id": device_id,
            "name": "Test Sensor",
            "device_type": "temperature_sensor",
        },
    )

    assert response.status_code == 201

    token_response = client.post(
        f"/devices/{device_id}/token"
    )

    assert token_response.status_code == 200

    return token_response.json()["token"]


def telemetry_payload(
    device_id: str = "sensor-401",
    idempotency_key: str = "reading-001",
) -> dict[str, object]:
    return {
        "device_id": device_id,
        "temperature": 72.5,
        "pressure": 101.3,
        "recorded_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "idempotency_key": idempotency_key,
    }


def test_ingest_telemetry(
    client: TestClient,
) -> None:
    token = register_device(client)

    response = client.post(
        "/telemetry",
        json=telemetry_payload(),
        headers=authorization_headers(token),
    )

    assert response.status_code == 201

    response_body = response.json()

    assert response_body["reading_id"] is not None
    assert response_body["device_id"] == "sensor-401"
    assert response_body["temperature"] == 72.5
    assert response_body["pressure"] == 101.3
    assert response_body["idempotency_key"] == "reading-001"
    assert response_body["received_at"] is not None
   


def test_ingest_telemetry_updates_last_seen(
    client: TestClient,
) -> None:
    token = register_device(client)

    ingestion_response = client.post(
        "/telemetry",
        json=telemetry_payload(),
        headers=authorization_headers(token),
    )

    device_response = client.get(
        "/devices/sensor-401",
    )

    assert ingestion_response.status_code == 201
    assert device_response.status_code == 200
    assert (
        device_response.json()["last_seen_at"]
        is not None
    )



def test_reject_telemetry_for_unknown_device(
    client: TestClient,
) -> None:
    token = register_device(client)

    response = client.post(
        "/telemetry",
        json=telemetry_payload(
            device_id="unknown-device"
        ),
        headers=authorization_headers(token),

    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": (
            "Device 'unknown-device' was not found."
        )
    }


def test_reject_telemetry_for_inactive_device(
    client: TestClient,
) -> None:
    token = register_device(client)

    status_response = client.patch(
        "/devices/sensor-401/status",
        json={
            "status": "inactive",
        },
        headers=authorization_headers(token),

    )

    response = client.post(
        "/telemetry",
        json=telemetry_payload(),
        headers=authorization_headers(token),
    )

    assert status_response.status_code == 200
    assert response.status_code == 409
    assert response.json() == {
        "detail": (
            "Device 'sensor-401' is inactive "
            "and cannot submit telemetry."
        )
    }


def test_reject_duplicate_idempotency_key(
    client: TestClient,
) -> None:
    token = register_device(client)

    payload = telemetry_payload()

    first_response = client.post(
        "/telemetry",
        json=payload,
        headers=authorization_headers(token),
    )

    second_response = client.post(
        "/telemetry",
        json=payload,
        headers=authorization_headers(token),

    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409

    assert second_response.json() == {
        "detail": (
            "Telemetry already exists for "
            "device 'sensor-401' with idempotency key "
            "'reading-001'."
        )
    }


def test_list_device_telemetry(
    client: TestClient,
) -> None:
    token = register_device(client)

    client.post(
        "/telemetry",
        json=telemetry_payload(
            idempotency_key="reading-001"
        ),
        headers=authorization_headers(token),
    )

    client.post(
        "/telemetry",
        json=telemetry_payload(
            idempotency_key="reading-002"
        ),
        headers=authorization_headers(token),
    )

    response = client.get(
        "/telemetry/sensor-401"
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_reject_future_timestamp(
    client: TestClient,
) -> None:
    token = register_device(client)

    payload = telemetry_payload()

    payload["recorded_at"] = (
        datetime.now(timezone.utc)
        + timedelta(minutes=10)
    ).isoformat()

    response = client.post(
        "/telemetry",
        json=payload,
        headers=authorization_headers(token),
    )

    assert response.status_code == 422


def test_reject_timestamp_without_timezone(
    client: TestClient,
) -> None:
    token = register_device(client)

    payload = telemetry_payload()

    payload["recorded_at"] = (
        datetime.now().replace(
            microsecond=0
        ).isoformat()
    )

    response = client.post(
        "/telemetry",
        json=payload,
        headers=authorization_headers(token),
    )

    assert response.status_code == 422


def test_reject_out_of_range_temperature(
    client: TestClient,
) -> None:
    token = register_device(client)

    payload = telemetry_payload()
    payload["temperature"] = 500.0

    response = client.post(
        "/telemetry",
        json=payload,
        headers=authorization_headers(token),
    )

    assert response.status_code == 422


def test_get_telemetry_for_unknown_device(
    client: TestClient,
) -> None:
    response = client.get(
        "/telemetry/unknown-device"
    )

    assert response.status_code == 404