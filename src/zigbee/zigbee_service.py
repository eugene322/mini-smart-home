import logging
import uuid
from typing import Dict

from gmqtt import Client as MQTTClient

logger = logging.getLogger(__name__)


class ZigbeeService:
    def __init__(self, host: str, port: int, username: str, password: str):
        self._client = MQTTClient(uuid.uuid4().hex)
        self._client.set_auth_credentials(username, password)
        self._host = host
        self._port = port

    async def _send_data(self, topic: str, payload: Dict):
        try:
            await self._client.connect(self._host, self._port)
            self._client.publish(topic, payload)
        finally:
            await self._client.disconnect()
