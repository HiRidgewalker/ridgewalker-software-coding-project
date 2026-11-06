"""仅在应用启动时声明固定的 RabbitMQ 拓扑。"""

from __future__ import annotations

import logging
import time

import pika

from app.rabbitmq import close_connection, create_connection
from app.settings import Settings

logger = logging.getLogger(__name__)


class TopologyInitializationError(RuntimeError):
    """应用无法以所需的 RabbitMQ 拓扑启动。"""


def declare_topology(settings: Settings) -> None:
    """一次性声明固定的交换机、队列和绑定关系。

    当已有资源的属性相同时，RabbitMQ 声明操作具有幂等性。因此这里不会先额外
    查询资源是否存在，再决定是否创建。
    """

    connection = create_connection(settings)
    try:
        channel = connection.channel()
        channel.exchange_declare(
            exchange=settings.rabbitmq_exchange,
            exchange_type=settings.rabbitmq_exchange_type,
            durable=True,
        )
        channel.queue_declare(queue=settings.rabbitmq_queue, durable=True)
        channel.queue_bind(
            queue=settings.rabbitmq_queue,
            exchange=settings.rabbitmq_exchange,
            routing_key=settings.rabbitmq_binding_key,
        )
    finally:
        close_connection(connection)


def initialize_topology(settings: Settings) -> None:
    """仅在消息代理尚未就绪时重试瞬时连接失败。"""

    last_error: pika.exceptions.AMQPConnectionError | None = None
    for attempt in range(1, settings.topology_initialization_attempts + 1):
        try:
            declare_topology(settings)
            logger.info(
                "RabbitMQ 拓扑已就绪：交换机=%s，队列=%s，绑定键=%s",
                settings.rabbitmq_exchange,
                settings.rabbitmq_queue,
                settings.rabbitmq_binding_key,
            )
            return
        except pika.exceptions.AMQPConnectionError as exc:
            last_error = exc
            if attempt == settings.topology_initialization_attempts:
                break
            logger.warning(
                "RabbitMQ 尚未就绪（第 %s/%s 次尝试），将在 %.1f 秒后重试",
                attempt,
                settings.topology_initialization_attempts,
                settings.topology_initialization_retry_seconds,
            )
            time.sleep(settings.topology_initialization_retry_seconds)
        except pika.exceptions.AMQPError as exc:
            raise TopologyInitializationError(
                "RabbitMQ 拒绝了当前拓扑配置。请检查已有资源是否使用了相同的类型和"
                "持久化设置。"
            ) from exc

    raise TopologyInitializationError(
        "初始化应用拓扑时 RabbitMQ 不可用。"
    ) from last_error
