from datetime import timedelta
from functools import lru_cache
from urllib.parse import quote

from celery import Celery
from kombu import Exchange, Queue
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

TASK_EXCHANGE_NAME = "celery.tasks.direct"
ASYNC_QUEUE_NAME = "celery.async.queue"
ASYNC_ROUTING_KEY = "celery.async"
SCHEDULED_QUEUE_NAME = "celery.scheduled.queue"
SCHEDULED_ROUTING_KEY = "celery.scheduled"

# 第一版保留既有协议名称，避免迁移前已入队的消息失去对应 Task。
PROCESS_MESSAGE_TASK_NAME = "app.tasks.async.process_message"
HEARTBEAT_TASK_NAME = "app.tasks.scheduled.heartbeat"

TASK_EXCHANGE = Exchange(TASK_EXCHANGE_NAME, type="direct", durable=True)

TASK_QUEUES = (
    Queue(
        ASYNC_QUEUE_NAME,
        exchange=TASK_EXCHANGE,
        routing_key=ASYNC_ROUTING_KEY,
        durable=True,
    ),
    Queue(
        SCHEDULED_QUEUE_NAME,
        exchange=TASK_EXCHANGE,
        routing_key=SCHEDULED_ROUTING_KEY,
        durable=True,
    ),
)

TASK_ROUTES = {
    "app.tasks.async.*": {
        "queue": ASYNC_QUEUE_NAME,
        "routing_key": ASYNC_ROUTING_KEY,
    },
    "app.tasks.scheduled.*": {
        "queue": SCHEDULED_QUEUE_NAME,
        "routing_key": SCHEDULED_ROUTING_KEY,
    },
}

TASK_IMPORTS = (
    "src.task.async_task",
    "src.task.scheduled_task",
)

BEAT_SCHEDULE = {
    "example-heartbeat-every-five-seconds": {
        "task": HEARTBEAT_TASK_NAME,
        "schedule": timedelta(seconds=5),
        "options": {
            "queue": SCHEDULED_QUEUE_NAME,
            "routing_key": SCHEDULED_ROUTING_KEY,
        },
    },
}


class CelerySettings(BaseSettings):
    """加载 RabbitMQ 连接信息和 Celery 环境配置。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    rabbitmq_host: str = "127.0.0.1"
    rabbitmq_port: int = Field(default=5672, ge=1, le=65535)
    rabbitmq_user: str
    rabbitmq_password: str
    rabbitmq_vhost: str = "/"

    celery_timezone: str = "Asia/Shanghai"
    celery_task_always_eager: bool = False
    declare_topology_on_startup: bool = True

    @property
    def broker_url(self) -> str:
        """构造经过转义的 RabbitMQ broker URL。"""

        username = quote(self.rabbitmq_user, safe="")
        password = quote(self.rabbitmq_password, safe="")
        virtual_host = quote(self.rabbitmq_vhost, safe="")
        return (
            f"amqp://{username}:{password}@{self.rabbitmq_host}:{self.rabbitmq_port}/{virtual_host}"
        )


@lru_cache
def get_celery_settings() -> CelerySettings:
    """返回进程内唯一的 Celery 配置对象。"""

    return CelerySettings()


def create_celery_app(settings: CelerySettings) -> Celery:
    """创建并完成项目级配置的 Celery 应用。"""

    application = Celery(
        "fastapi_celery_template",
        broker=settings.broker_url,
    )
    application.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone=settings.celery_timezone,
        enable_utc=True,
        task_ignore_result=True,
        task_create_missing_queues=False,
        task_default_queue=ASYNC_QUEUE_NAME,
        task_default_exchange=TASK_EXCHANGE_NAME,
        task_default_exchange_type="direct",
        task_default_routing_key=ASYNC_ROUTING_KEY,
        worker_prefetch_multiplier=1,
        broker_connection_retry_on_startup=True,
        task_queues=TASK_QUEUES,
        task_routes=TASK_ROUTES,
        beat_schedule=BEAT_SCHEDULE,
        imports=TASK_IMPORTS,
        task_always_eager=settings.celery_task_always_eager,
        task_eager_propagates=settings.celery_task_always_eager,
    )
    return application


celery_settings = get_celery_settings()
celery_app = create_celery_app(celery_settings)
