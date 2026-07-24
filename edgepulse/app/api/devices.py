from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from edgepulse.app.database.session import get_db
from edgepulse.app.models.device import (
    DeviceCreate,
    DeviceResponse,
)
from edgepulse.app.services.device_exceptions import (
    DeviceAlreadyExistsError,
    DeviceNotFoundError,
)
from edgepulse.app.services.device_service import DeviceService


router = APIRouter(
    prefix="/devices",
    tags=["devices"],
)


@router.post(
    "",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_device(
    request: DeviceCreate,
    database: Session = Depends(get_db),
) -> DeviceResponse:
    try:
        device = DeviceService.register_device(
            database=database,
            request=request,
        )

        return DeviceResponse.model_validate(device)

    except DeviceAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get(
    "/{device_id}",
    response_model=DeviceResponse,
)
def get_device(
    device_id: str,
    database: Session = Depends(get_db),
) -> DeviceResponse:
    try:
        device = DeviceService.get_device(
            database=database,
            device_id=device_id,
        )

        return DeviceResponse.model_validate(device)

    except DeviceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "",
    response_model=list[DeviceResponse],
)
def list_devices(
    database: Session = Depends(get_db),
) -> list[DeviceResponse]:
    devices = DeviceService.list_devices(database)

    return [
        DeviceResponse.model_validate(device)
        for device in devices
    ]