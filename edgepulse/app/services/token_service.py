import hashlib
import secrets
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from edgepulse.app.database.device_entity import DeviceEntity
from edgepulse.app.services.device_exceptions import (
    DeviceNotFoundError,
)


class TokenService:
    @staticmethod
    def hash_token(token: str) -> str:
        return hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def issue_token(
        database: Session,
        device_id: str,
    ) -> tuple[str, datetime]:
        device = database.get(
            DeviceEntity,
            device_id,
        )

        if device is None:
            raise DeviceNotFoundError(device_id)

        raw_token = secrets.token_urlsafe(32)
        issued_at = datetime.now(timezone.utc)

        device.token_hash = TokenService.hash_token(
            raw_token
        )
        device.token_issued_at = issued_at

        database.commit()
        database.refresh(device)

        return raw_token, issued_at

    @staticmethod
    def token_matches(
        device: DeviceEntity,
        raw_token: str,
    ) -> bool:
        if device.token_hash is None:
            return False

        supplied_hash = TokenService.hash_token(
            raw_token
        )

        return secrets.compare_digest(
            supplied_hash,
            device.token_hash,
        )