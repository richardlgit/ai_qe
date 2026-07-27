from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from edgepulse.app.database.config import Base


class AlertEntity(Base):
    __tablename__ = "alerts"

    alert_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    device_id: Mapped[str] = mapped_column(
        ForeignKey("devices.device_id"),
        nullable=False,
        index=True,
    )

    reading_id: Mapped[str] = mapped_column(
        ForeignKey("telemetry_readings.reading_id"),
        nullable=False,
        index=True,
    )

    alert_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    measured_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    threshold_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    acknowledged: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )