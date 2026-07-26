import pytest
from sqlalchemy.orm import Session

from edgepulse.app.models.device import (
    DeviceCreate,
    DeviceStatus,
    DeviceStatusUpdate,
)
from edgepulse.app.services.device_exceptions import (
    DeviceNotFoundError,
)
from edgepulse.app.services.device_service import DeviceService


def test_device_service_updates_status(
    database: Session,
) -> None:
    device = DeviceService.register_device(
        database=database,
        request=DeviceCreate(
            device_id="sensor-301",
            name="Cooling System Sensor",
            device_type="temperature_sensor",
        ),
    )

    updated_device = DeviceService.update_device_status(
        database=database,
        device_id=device.device_id,
        request=DeviceStatusUpdate(
            status=DeviceStatus.INACTIVE,
        ),
    )

    assert updated_device.status == "inactive"


def test_device_service_rejects_unknown_device(
    database: Session,
) -> None:
    with pytest.raises(DeviceNotFoundError):
        DeviceService.update_device_status(
            database=database,
            device_id="missing-device",
            request=DeviceStatusUpdate(
                status=DeviceStatus.INACTIVE,
            ),
        )