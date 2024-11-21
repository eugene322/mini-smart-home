from typing import Dict, Any, List

from jobs.devices import device_state_changed
from jobs.queues_service import QueuesService
from services.storage_service import StorageService
from zigbee.models import DeviceState, DevicePayload
from zigbee.zigbee_worker import ZigbeeWorker
from zigbee.constants import QUEUES_SERVICE, STORAGE_SERVICE


def on_device_state(service: ZigbeeWorker, name: str, device_state: DeviceState, dep: Dict[str, Any]) -> None:
    print(name)
    print(device_state)

    qs: QueuesService = dep[QUEUES_SERVICE]
    qs.default(device_state_changed, name, device_state.model_dump(mode="json"))


def on_devices(service: ZigbeeWorker, devices: List[DevicePayload], dep: Dict[str, Any]) -> None:
    ss: StorageService = dep[STORAGE_SERVICE]

    old_devices = [DevicePayload.model_validate(d) for d in ss.get_devices_data()]
    print(old_devices)
    old_devices_names = {o.friendly_name for o in old_devices}
    print(old_devices_names)
    devices_names = {o.friendly_name for o in devices}
    print(devices_names)

    to_remove = old_devices_names - devices_names
    print(to_remove)
    for name in to_remove:
        service.unsubscribe_from_device(name)

    to_add = devices_names - old_devices_names
    print(to_add)
    for name in to_add:
        service.subscribe_on_device(name)

    ss.set_devices_data([d.model_dump(mode="json") for d in devices])