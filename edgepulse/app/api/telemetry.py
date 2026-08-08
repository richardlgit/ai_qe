from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    status,
)
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
from edgepulse.app.database.device_entity import DeviceEntity
from edgepulse.app.services.auth_exceptions import (
    InvalidDeviceTokenError,
    MissingDeviceTokenError,
)
from edgepulse.app.services.token_service import TokenService

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
    authorization: str | None = Header(
        default=None
    ),
    database: Session = Depends(get_db),
) -> TelemetryResponse:
    try:
        raw_token = extract_bearer_token(
            authorization
        )

        device = database.get(
            DeviceEntity,
            request.device_id,
        )

        if device is None:
            raise DeviceNotFoundError(
                request.device_id
            )

        if not TokenService.token_matches(
            device=device,
            raw_token=raw_token,
        ):
            raise InvalidDeviceTokenError(
                request.device_id
            )

        telemetry = TelemetryService.ingest_telemetry(
            database=database,
            request=request,
        )

        return TelemetryResponse.model_validate(
            telemetry
        )
    except MissingDeviceTokenError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={
                "WWW-Authenticate": "Bearer"
            },
    ) from error

    except InvalidDeviceTokenError as error:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={
            "WWW-Authenticate": "Bearer"
        },
    ) from error
    
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
    
def extract_bearer_token(
    authorization: str | None,
) -> str:
    if authorization is None:
        raise MissingDeviceTokenError()

    scheme, separator, token = authorization.partition(
        " "
    )

    if (
        separator == ""
        or scheme.lower() != "bearer"
        or not token.strip()
    ):
        raise MissingDeviceTokenError()

    return token.strip()


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