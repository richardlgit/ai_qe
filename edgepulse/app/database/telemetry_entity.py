from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from edgepulse.app.database.config import Base


class TelemetryEntity(Base):
    __tablename__ = "telemetry_readings"

    __table_args__ = (
        UniqueConstraint(
            "device_id",
            "idempotency_key",
            name="uq_telemetry_device_idempotency_key",
        ),
    )

    reading_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    device_id: Mapped[str] = mapped_column(
        ForeignKey("devices.device_id"),
        nullable=False,
        index=True,
    )

    temperature: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    pressure: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    idempotency_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )