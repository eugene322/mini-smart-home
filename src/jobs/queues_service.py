from redis import Redis
from rq import Queue
from rq.job import Job


class QueuesService:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis
        self._default_q = Queue(connection=redis)

    def default(self, func, *args, **kwargs) -> str:
        job = Job.create(func, connection=self._redis, args=args, kwargs=kwargs)
        self._default_q.enqueue(func, args=args, kwargs=kwargs)
        return job.id
