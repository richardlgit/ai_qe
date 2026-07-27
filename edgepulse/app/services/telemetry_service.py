from datetime import timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from edgepulse.app.database.device_entity import DeviceEntity
from edgepulse.app.database.telemetry_entity import TelemetryEntity
from edgepulse.app.models.device import DeviceStatus
from edgepulse.app.models.telemetry import TelemetryCreate
from edgepulse.app.services.device_exceptions import DeviceNotFoundError
from edgepulse.app.services.telemetry_exceptions import (
    DuplicateTelemetryError,
    InactiveDeviceError,
)
from edgepulse.app.services.alert_service import AlertService


class TelemetryService:
    @staticmethod
    def ingest_telemetry(
        database: Session,
        request: TelemetryCreate,
    ) -> TelemetryEntity:
        device = database.get(
            DeviceEntity,
            request.device_id,
        )

        if device is None:
            raise DeviceNotFoundError(request.device_id)

        if device.status != DeviceStatus.ACTIVE.value:
            raise InactiveDeviceError(request.device_id)

        duplicate_statement = select(TelemetryEntity).where(
            TelemetryEntity.device_id == request.device_id,
            TelemetryEntity.idempotency_key
            == request.idempotency_key,
        )

        duplicate = database.scalar(duplicate_statement)

        if duplicate is not None:
            raise DuplicateTelemetryError(
                device_id=request.device_id,
                idempotency_key=request.idempotency_key,
            )

        recorded_at = request.recorded_at.astimezone(
            timezone.utc
        )

        telemetry = TelemetryEntity(
            reading_id=str(uuid4()),
            device_id=request.device_id,
            temperature=request.temperature,
            pressure=request.pressure,
            recorded_at=recorded_at,
            idempotency_key=request.idempotency_key,
        )

        database.add(telemetry)

        device.last_seen_at = recorded_at

        AlertService.evaluate_temperature(
            database=database,
            telemetry=telemetry,
        )

        try:
            database.commit()   
        except IntegrityError as error:
            database.rollback()

            raise DuplicateTelemetryError(
                device_id=request.device_id,
                idempotency_key=request.idempotency_key,
            ) from error

        database.refresh(telemetry)

        return telemetry

    @staticmethod
    def list_device_telemetry(
        database: Session,
        device_id: str,
    ) -> list[TelemetryEntity]:
        device = database.get(DeviceEntity, device_id)

        if device is None:
            raise DeviceNotFoundError(device_id)

        statement = (
            select(TelemetryEntity)
            .where(
                TelemetryEntity.device_id == device_id
            )
            .order_by(
                TelemetryEntity.recorded_at.desc()
            )
        )

        return list(
            database.scalars(statement).all()
        )