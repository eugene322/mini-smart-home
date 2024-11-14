from typing import Dict, Any

from services.zigbee_service import ZigbeeService, DeviceState


def on_device_state(service: ZigbeeService, name: str, device_state: DeviceState, dep: Dict[str, Any]) -> None:
    print(name)
    print(device_state)