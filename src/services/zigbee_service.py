import asyncio
import json
import logging
import re
import signal
import uuid
from asyncio import Event
from collections.abc import Callable
from enum import Enum
from typing import Optional, Dict

from gmqtt import Client as MQTTClient
from gmqtt import Subscription

logger = logging.getLogger(__name__)


class ZigbeeEvent(Enum):
    DEVICES_UPDATED = 1
    DEVICE_STATE_CHANGED = 2


class ZigbeeService:
    ON_DEVICES = "zigbee2mqtt/bridge/devices/#"
    ON_DEVICE = "zigbee2mqtt/{friendly_name}/#"

    def __init__(self):
        self._stop_signal: Optional[Event] = None
        self._client: Optional[MQTTClient] = None
        self._handlers: Dict[ZigbeeEvent, Callable] = {}
        self._subscriptions: Dict[str, Subscription] = {}

    def register_handler(self, event_type: ZigbeeEvent, handler: Callable) -> None:
        self._handlers[event_type] = handler

    def _on_connect(self, client, flags, rc, properties) -> None:
        logger.info(f"On connect: {flags} {rc} {properties}")
        client.subscribe(self.ON_DEVICES, qos=2)

    def _on_disconnect(self, client, packet, exc=None) -> None:
        logger.info(f"On disconnect: {packet} {exc}")

    def _on_subscribe(self, client, mid, qos, properties) -> None:
        logger.info(f"On subscribe: {mid} {qos} {properties}")

    def _signal_stop_polling(self, *args) -> None:
        self._stop_signal.set()

    def _on_message(self, client, topic, payload, qos, properties) -> None:
        logger.info(f"On message {topic}: {payload}: {qos}: {properties}")
        json_payload = json.loads(payload)
        try:
            if topic == self.ON_DEVICES[:-2]:
                self._subscribe_on_devices(client, json_payload)
                handler = self._handlers.get(ZigbeeEvent.DEVICES_UPDATED)
                if handler:
                    handler(json_payload)
            elif topic == self.ON_DEVICE[:-2]:
                device_name = re.findall(r"zigbee2mqtt/(\w*)/", topic)
                handler = self._handlers.get(ZigbeeEvent.DEVICE_STATE_CHANGED)
                if handler:
                    handler(device_name, json_payload)
        except Exception as e:
            logger.error(e)

    def _subscribe_on_devices(self, client, devices_payload):
        new_devices_subscription = {}
        for device in devices_payload:
            device_topic = self.ON_DEVICE.format(friendly_name=device["friendly_name"])
            if device_topic in self._subscriptions:
                # Skip subscribed devices
                continue
            if device["type"] in ("Coordinator",):
                # Skip Coordinator
                continue
            new_devices_subscription[device_topic] = Subscription(
                topic=device_topic,
                qos=1
            )

        self._subscriptions.update(new_devices_subscription)
        client.subscribe(list(new_devices_subscription.values()))
        logger.info(f"Subscribed on new: {new_devices_subscription}")

    async def start_pooling(self, host: str, port: int, username: str, password: str):
        self._stop_signal = Event()
        self._stop_signal.clear()

        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGTERM, self._signal_stop_polling, signal.SIGTERM)
        loop.add_signal_handler(signal.SIGINT, self._signal_stop_polling, signal.SIGINT)

        try:
            self._client = MQTTClient(uuid.uuid4().hex)

            self._client.on_connect = self._on_connect
            self._client.on_disconnect = self._on_disconnect
            self._client.on_subscribe = self._on_subscribe
            self._client.on_message = self._on_message

            self._client.set_auth_credentials(username, password)
            await self._client.connect(host, port)
            await self._stop_signal.wait()
        finally:
            await self._client.disconnect()
