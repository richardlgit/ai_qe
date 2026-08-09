from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from edgepulse.app.database.alert_entity import AlertEntity
from edgepulse.app.database.telemetry_entity import TelemetryEntity
from edgepulse.app.models.alert import (
    AlertSeverity,
    AlertType,
)
from edgepulse.app.services.alert_config import (
    CRITICAL_TEMPERATURE_THRESHOLD,
)
from edgepulse.app.services.alert_exceptions import (
    AlertNotFoundError,
)


class AlertService:
    @staticmethod
    def evaluate_temperature(
        database: Session,
        telemetry: TelemetryEntity,
    ) -> AlertEntity | None:
        threshold = CRITICAL_TEMPERATURE_THRESHOLD

        if telemetry.temperature <= threshold:
            return None

        alert = AlertEntity(
            alert_id=str(uuid4()),
            device_id=telemetry.device_id,
            reading_id=telemetry.reading_id,
            alert_type=AlertType.HIGH_TEMPERATURE.value,
            severity=AlertSeverity.CRITICAL.value,
            message=(
                f"Temperature {telemetry.temperature} "
                f"reached or exceeded critical threshold "
                f"{threshold}."
            ),
            measured_value=telemetry.temperature,
            threshold_value=threshold,
            acknowledged=False,
        )

        database.add(alert)

        return alert

    @staticmethod
    def list_alerts(
        database: Session,
        acknowledged: bool | None = None,
    ) -> list[AlertEntity]:
        statement = select(AlertEntity)

        if acknowledged is not None:
            statement = statement.where(
                AlertEntity.acknowledged == acknowledged
            )

        statement = statement.order_by(
            AlertEntity.created_at.desc(),
            AlertEntity.alert_id,
        )

        return list(
            database.scalars(statement).all()
        )

    @staticmethod
    def get_alert(
        database: Session,
        alert_id: str,
    ) -> AlertEntity:
        alert = database.get(AlertEntity, alert_id)

        if alert is None:
            raise AlertNotFoundError(alert_id)

        return alert

    @staticmethod
    def acknowledge_alert(
        database: Session,
        alert_id: str,
    ) -> AlertEntity:
        alert = database.get(AlertEntity, alert_id)

        if alert is None:
            raise AlertNotFoundError(alert_id)

        if not alert.acknowledged:
            alert.acknowledged = True
            alert.acknowledged_at = datetime.now(
                timezone.utc
            )

            database.commit()
            database.refresh(alert)

        return alert