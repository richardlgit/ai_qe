from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from edgepulse.app.database.session import get_db
from edgepulse.app.models.telemetry import (
    TelemetryCreate,
    TelemetryResponse,
)
from edgepulse.app.services.device_exceptions import DeviceNotFoundError
from edgepulse.app.services.telemetry_exceptions import (
    DuplicateTelemetryError,
    InactiveDeviceError,
)
from edgepulse.app.services.telemetry_service import TelemetryService


router = APIRouter(
    prefix="/telemetry",
    tags=["telemetry"],
)


@router.post(
    "",
    response_model=TelemetryResponse,
    status_code=status.HTTP_201_CREATED,
)
def ingest_telemetry(
    request: TelemetryCreate,
    database: Session = Depends(get_db),
) -> TelemetryResponse:
    try:
        telemetry = TelemetryService.ingest_telemetry(
            database=database,
            request=request,
        )

        return TelemetryResponse.model_validate(
            telemetry
        )

    except DeviceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except InactiveDeviceError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except DuplicateTelemetryError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get(
    "/{device_id}",
    response_model=list[TelemetryResponse],
)
def list_device_telemetry(
    device_id: str,
    database: Session = Depends(get_db),
) -> list[TelemetryResponse]:
    try:
        readings = (
            TelemetryService.list_device_telemetry(
                database=database,
                device_id=device_id,
            )
        )

        return [
            TelemetryResponse.model_validate(
                reading
            )
            for reading in readings
        ]

    except DeviceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error