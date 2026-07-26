from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TelemetryCreate(BaseModel):
    device_id: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
    )

    temperature: float = Field(
        ge=-100.0,
        le=300.0,
    )

    pressure: float = Field(
        ge=0.0,
        le=5000.0,
    )

    recorded_at: datetime

    idempotency_key: str = Field(
        min_length=1,
        max_length=100,
    )

    @field_validator("recorded_at")
    @classmethod
    def validate_recorded_at(
        cls,
        value: datetime,
    ) -> datetime:
        if value.tzinfo is None:
            raise ValueError(
                "recorded_at must include timezone information"
            )

        now = datetime.now(timezone.utc)

        if value > now + timedelta(minutes=5):
            raise ValueError(
                "recorded_at cannot be more than five minutes in the future"
            )

        return value


class TelemetryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reading_id: str
    device_id: str
    temperature: float
    pressure: float
    recorded_at: datetime
    received_at: datetime
    idempotency_key: str