import asyncio
import logging
import re
import signal
import uuid
from asyncio import Event
from collections.abc import Callable
from enum import Enum
from typing import Optional, Dict, Any, List

from gmqtt import Client as MQTTClient
from gmqtt import Subscription
from pydantic import BaseModel, ConfigDict
from pydantic_core import from_json

logger = logging.getLogger(__name__)


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

class ZigbeeService:
    ON_DEVICES = "zigbee2mqtt/bridge/devices/#"
    ON_DEVICE = "zigbee2mqtt/{friendly_name}/#"
    ON_DEVICE_RE = r"zigbee2mqtt/([\d|\w|\-|_]+)"

    def __init__(self):
        self._stop_signal: Optional[Event] = None
        self._client: Optional[MQTTClient] = None
        self._handlers: Dict[ZigbeeEvent, Callable] = {}
        self._subscriptions: Dict[str, Subscription] = {}
        self._dep: Dict[str, Any] = {}

    def register_handler(self, event_type: ZigbeeEvent, handler: Callable) -> None:
        self._handlers[event_type] = handler

    def register_dep(self, name: str, dep: Any) -> None:
        self._dep[name] = dep

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
        payload = from_json(payload)
        try:
            if topic == self.ON_DEVICES[:-2]:
                handler = self._handlers.get(ZigbeeEvent.DEVICES_UPDATED)
                device_payloads = [DevicePayload.model_validate(p) for p in payload]
                if handler:
                    handler(self, device_payloads, self._dep)
            elif re.match(self.ON_DEVICE_RE, topic):
                device_name = re.findall(self.ON_DEVICE_RE, topic)
                handler = self._handlers.get(ZigbeeEvent.DEVICE_STATE_CHANGED)
                device_state = DeviceState.model_validate(payload)
                if handler:
                    handler(self, device_name, device_state, self._dep)
            else:
                logger.error(f"Unknown topic: {topic}")
        except Exception as e:
            logger.error(e)

    def subscribe_on_device(self, friendly_name: str):
        device_topic = self.ON_DEVICE.format(friendly_name=friendly_name)
        if device_topic in self._subscriptions:
            # Skip subscribed devices
            logger.warning(f"Skipped: {friendly_name}")
            return None

        self._subscriptions[device_topic] = Subscription(topic=device_topic, qos=1)
        self._client.subscribe(self._subscriptions[device_topic])
        logger.info(f"Subscribed on new: {device_topic}")

    def unsubscribe_from_device(self, friendly_name: str):
        device_topic = self.ON_DEVICE.format(friendly_name=friendly_name)
        subscription = self._subscriptions.pop(device_topic)
        if subscription:
            # Skip subscribed devices
            logger.error(f"Skipped: {friendly_name}")
            return None

        self._client.unsubscribe(subscription.topic)
        logger.info(f"Unsubscribe from: {device_topic}")

    def subscriptions(self) -> List[str]:
        return list(self._subscriptions.keys())

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
