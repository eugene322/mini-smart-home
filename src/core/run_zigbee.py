import asyncio
import logging
import sys

from core.settings import Settings
from services.zigbee_service import ZigbeeService, ZigbeeEvent
from zigbee.handlers.device_state import on_device_state
from zigbee.handlers.devices import on_devices


async def main():
    settings = Settings()
    service = ZigbeeService()

    service.register_handler(ZigbeeEvent.DEVICES_UPDATED, on_devices)
    service.register_handler(ZigbeeEvent.DEVICE_STATE_CHANGED, on_device_state)

    await service.start_pooling(
        settings.mqtt_host,
        settings.mqtt_port,
        settings.mqtt_user,
        settings.mqtt_password,
    )


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())