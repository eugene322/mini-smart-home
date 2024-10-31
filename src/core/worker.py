from redis import Redis
from rq import Worker

from core.settings import Settings

settings = Settings()

queues = ["default"]

connection=Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    password=settings.redis_password
)

worker = Worker(queues, connection=connection)
worker.work()
