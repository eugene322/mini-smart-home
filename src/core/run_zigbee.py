import asyncio
import logging
import sys

from redis import Redis

from core.settings import Settings
from jobs.queues_service import QueuesService
from services.storage_service import StorageService
from zigbee.models import ZigbeeEvent
from zigbee.zigbee_worker import ZigbeeWorker
from zigbee.constants import QUEUES_SERVICE, STORAGE_SERVICE
from zigbee.handlers import on_device_state, on_devices


async def main():
    settings = Settings()
    service = ZigbeeWorker()

    service.register_dep(
        QUEUES_SERVICE,
        QueuesService(
            redis=Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password
            )
        )
    )
    storage = StorageService(
        redis=Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password
        )
    )
    storage.set_devices_data([])
    service.register_dep(STORAGE_SERVICE, storage)

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