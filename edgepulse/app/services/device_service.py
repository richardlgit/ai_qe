from sqlalchemy import select
from sqlalchemy.orm import Session

from edgepulse.app.database.device_entity import DeviceEntity
from edgepulse.app.models.device import DeviceCreate, DeviceStatus
from edgepulse.app.services.device_exceptions import (
    DeviceAlreadyExistsError,
    DeviceNotFoundError,
)


class DeviceService:
    @staticmethod
    def register_device(
        database: Session,
        request: DeviceCreate,
    ) -> DeviceEntity:
        existing_device = database.get(
            DeviceEntity,
            request.device_id,
        )

        if existing_device is not None:
            raise DeviceAlreadyExistsError(request.device_id)

        device = DeviceEntity(
            device_id=request.device_id,
            name=request.name,
            device_type=request.device_type,
            status=DeviceStatus.ACTIVE.value,
        )

        database.add(device)
        database.commit()
        database.refresh(device)

        return device

    @staticmethod
    def get_device(
        database: Session,
        device_id: str,
    ) -> DeviceEntity:
        device = database.get(DeviceEntity, device_id)

        if device is None:
            raise DeviceNotFoundError(device_id)

        return device

    @staticmethod
    def list_devices(
        database: Session,
    ) -> list[DeviceEntity]:
        statement = select(DeviceEntity).order_by(
            DeviceEntity.registered_at,
            DeviceEntity.device_id,
        )

        return list(database.scalars(statement).all())