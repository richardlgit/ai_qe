from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from edgepulse.app.database.device_entity import DeviceEntity
from edgepulse.app.database.telemetry_entity import TelemetryEntity
from edgepulse.app.services.alert_service import AlertService


def create_telemetry(
    database: Session,
    temperature: float,
) -> TelemetryEntity:
    device = DeviceEntity(
        device_id=f"sensor-{uuid4()}",
        name="Boundary Test Sensor",
        device_type="temperature_sensor",
        status="active",
    )

    database.add(device)
    database.flush()

    telemetry = TelemetryEntity(
        reading_id=str(uuid4()),
        device_id=device.device_id,
        temperature=temperature,
        pressure=101.3,
        recorded_at=datetime.now(timezone.utc),
        idempotency_key=str(uuid4()),
    )

    database.add(telemetry)
    database.flush()

    return telemetry


def test_no_alert_below_critical_threshold(
    database: Session,
) -> None:
    telemetry = create_telemetry(
        database=database,
        temperature=99.9,
    )

    alert = AlertService.evaluate_temperature(
        database=database,
        telemetry=telemetry,
    )

    assert alert is None


def test_alert_created_at_critical_threshold(
    database: Session,
) -> None:
    telemetry = create_telemetry(
        database=database,
        temperature=100.0,
    )

    alert = AlertService.evaluate_temperature(
        database=database,
        telemetry=telemetry,
    )

    assert alert is not None
    assert alert.measured_value == 100.0
    assert alert.threshold_value == 100.0


def test_alert_created_above_critical_threshold(
    database: Session,
) -> None:
    telemetry = create_telemetry(
        database=database,
        temperature=100.1,
    )

    alert = AlertService.evaluate_temperature(
        database=database,
        telemetry=telemetry,
    )

    assert alert is not None