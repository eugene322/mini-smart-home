import json
from typing import List, Dict

from redis import Redis


class StorageService:
    DEVICES_KEY: str = "devices_data"

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    def set_devices_data(self, devices_data: List[Dict]) -> None:
        self._redis.set(self.DEVICES_KEY, json.dumps(devices_data))

    def get_devices_data(self) -> List[Dict]:
        raw_value = self._redis.get(self.DEVICES_KEY)
        return json.loads(raw_value) if raw_value else []