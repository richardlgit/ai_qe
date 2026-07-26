from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class DeviceStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class DeviceCreate(BaseModel):
    device_id: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
    )

    name: str = Field(
        min_length=1,
        max_length=100,
    )

    device_type: str = Field(
        min_length=1,
        max_length=50,
    )

class DeviceStatusUpdate(BaseModel):
    status: DeviceStatus
    
class DeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    device_id: str
    name: str
    device_type: str
    status: DeviceStatus
    registered_at: datetime
    last_seen_at: datetime | None