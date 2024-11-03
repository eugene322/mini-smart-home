from typing import Dict

def on_device_state(name: str, payload: Dict) -> None:
    print(name)
    print(payload)