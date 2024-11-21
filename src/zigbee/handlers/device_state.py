from typing import Dict, Any

from jobs.devices import device_state_changed
from jobs.queues_service import QueuesService
from zigbee.zigbee_service import ZigbeeService, DeviceState
from zigbee.constants import QUEUES_SERVICE


def on_device_state(service: ZigbeeService, name: str, device_state: DeviceState, dep: Dict[str, Any]) -> None:
    print(name)
    print(device_state)

    qs: QueuesService = dep[QUEUES_SERVICE]
    qs.default(device_state_changed,name, device_state.model_dump(mode="json") )
