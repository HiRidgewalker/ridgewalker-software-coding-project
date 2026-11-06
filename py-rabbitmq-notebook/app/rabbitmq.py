"""RabbitMQ 连接和消息发布辅助函数。

本模块刻意不包含拓扑声明。相关操作统一放在 app.topology 中，只会由
FastAPI 启动钩子调用。
"""

from __future__ import annotations

import pika

from app.models import MessageEnvelope
from app.settings import Settings


class RabbitMQPublishError(RuntimeError):
    """RabbitMQ 未能接收消息发布。"""


class MessageUnroutableError(RabbitMQPublishError):
    """没有队列绑定关系匹配该消息的路由键。"""


def create_connection(settings: Settings) -> pika.BlockingConnection:
    """为当前进程操作打开新的阻塞连接。"""

    return pika.BlockingConnection(settings.connection_parameters)


def close_connection(connection: pika.BlockingConnection | None) -> None:
    """关闭连接，同时不掩盖原始操作错误。"""

    if connection is not None and connection.is_open:
        try:
            connection.close()
        except pika.exceptions.AMQPError:
            pass


def publish_message(settings: Settings, message: MessageEnvelope) -> None:
    """发布一条持久化 JSON 消息，并等待消息代理确认。"""

    # 预先设为 None，保证连接创建失败时 finally 仍可安全执行。
    connection: pika.BlockingConnection | None = None
    try:
        # 根据配置建立到 RabbitMQ 的 TCP / AMQP 连接。
        connection = create_connection(settings)

        # 在连接上创建 Channel；实际发布操作通过 Channel 完成。
        channel = connection.channel()

        # 开启发布者确认模式，后续 basic_publish 会等待 RabbitMQ 确认或拒绝消息。
        channel.confirm_delivery()

        # 向指定交换机发布消息。
        channel.basic_publish(
            # 目标交换机，例如 orders.direct。
            exchange=settings.rabbitmq_exchange,

            # 路由键，例如 order.created。direct 交换机会将它与 binding_key 完全匹配。
            routing_key=message.routing_key,

            # 将 Pydantic 模型序列化为 JSON，再编码为 UTF-8 字节。
            # RabbitMQ 的消息体本质上是 bytes。
            body=message.model_dump_json().encode("utf-8"),

            # 设置 AMQP 消息属性。
            properties=pika.BasicProperties(
                # 声明消息体类型，便于消费者识别。
                content_type="application/json",

                # 2 表示持久化消息；配合 durable Queue，可在 RabbitMQ 重启后恢复。
                delivery_mode=2,

                # 写入业务消息唯一标识，便于日志追踪、幂等处理和排查重复消费。
                message_id=str(message.message_id),

                # 将消息创建时间转换为 Unix 时间戳，单位为秒。
                timestamp=int(message.published_at.timestamp()),
            ),

            # 没有任何 Queue 匹配时，要求 RabbitMQ 将消息退回给发布端。
            # 配合发布者确认模式，Pika 会抛出 UnroutableError。
            mandatory=True,
        )

    # 专门处理“路由键没有匹配到任何绑定关系”的情况。
    except pika.exceptions.UnroutableError as exc:
        raise MessageUnroutableError(
            f"没有绑定关系接收 routing_key={message.routing_key!r} 的消息。"
        ) from exc

    # 处理其他 RabbitMQ / AMQP 异常，例如连接失败或 Channel 异常。
    except pika.exceptions.AMQPError as exc:
        raise RabbitMQPublishError("RabbitMQ 无法发布该消息。") from exc

    # 无论发布成功还是失败，都关闭本次创建的连接。
    # close_connection 内部会判断连接是否存在、是否仍处于开启状态。
    finally:
        close_connection(connection)
