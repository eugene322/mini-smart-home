from redis import Redis


class QueuesService:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis