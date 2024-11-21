from typing import Dict


def send_device_info(chat_id: str, device_id: str) -> None:
    pass


def device_state_changed(device_name: str, state: Dict) -> None:
    print(device_name)
    print(state)