from enum import Enum

from pydantic import BaseModel, ConfigDict


class ZigbeeEvent(Enum):
    DEVICES_UPDATED = 1
    DEVICE_STATE_CHANGED = 2


class DevicePayload(BaseModel):
    friendly_name: str

    model_config = ConfigDict(
        extra="allow"
    )

class DeviceState(BaseModel):
    model_config = ConfigDict(
        extra="allow"
    )