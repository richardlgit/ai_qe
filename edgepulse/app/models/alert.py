from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class AlertType(str, Enum):
    HIGH_TEMPERATURE = "high_temperature"


class AlertSeverity(str, Enum):
    CRITICAL = "critical"


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    alert_id: str
    device_id: str
    reading_id: str
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    measured_value: float
    threshold_value: float
    created_at: datetime
    acknowledged: bool
    acknowledged_at: datetime | None