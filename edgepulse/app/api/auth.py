from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from edgepulse.app.database.device_entity import DeviceEntity
from edgepulse.app.database.session import get_db
from edgepulse.app.services.auth_exceptions import (
    InvalidDeviceTokenError,
    MissingDeviceTokenError,
)
from edgepulse.app.services.device_exceptions import (
    DeviceNotFoundError,
)
from edgepulse.app.services.token_service import TokenService


bearer_scheme = HTTPBearer(
    auto_error=False,
)


def authenticate_device(
    device_id: str,
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    database: Session = Depends(get_db),
) -> DeviceEntity:
    device = database.get(
        DeviceEntity,
        device_id,
    )

    if device is None:
        raise DeviceNotFoundError(device_id)

    if credentials is None:
        raise MissingDeviceTokenError()

    if credentials.scheme.lower() != "bearer":
        raise MissingDeviceTokenError()

    if not TokenService.token_matches(
        device=device,
        raw_token=credentials.credentials,
    ):
        raise InvalidDeviceTokenError(device_id)

    return device