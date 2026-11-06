"""由 Supervisor 独立守护的 RabbitMQ 消费者进程。

该进程刻意不声明或检查交换机、队列和绑定关系。这些资源由 FastAPI 启动阶段
统一管理。
"""

from __future__ import annotations

import logging
import signal
import sys
import time
from types import FrameType

import pika
from pydantic import ValidationError

from app.logging_utils import configure_logging
from app.models import MessageEnvelope
from app.rabbitmq import close_connection, create_connection
from app.settings import Settings, get_settings

configure_logging()
logger = logging.getLogger(__name__)


class OrderCreatedConsumer:
    """通过手动确认机制消费唯一的固定队列。"""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.connection: pika.BlockingConnection | None = None
        self.channel: pika.adapters.blocking_connection.BlockingChannel | None = None

    def run(self) -> None:
        """建立连接并持续消费，直到 Supervisor 要求进程停止。"""

        # 注册 SIGTERM 和 SIGINT 的处理函数，使 Supervisor 停止进程时能优雅结束消费。
        self._install_signal_handlers()
        # 根据配置创建到 RabbitMQ 的长连接，并保存到实例属性以便关闭时复用。
        self.connection = create_connection(self.settings)
        # 通过连接创建一个 AMQP 信道；发布、订阅和确认等操作都通过信道完成。
        self.channel = self.connection.channel()
        # 限制该消费者同时最多接收一条尚未确认的消息，形成公平分发并方便观察确认机制。
        self.channel.basic_qos(prefetch_count=1)
        # 向 RabbitMQ 登记当前消费者，并声明收到消息时应调用的回调函数。
        self.channel.basic_consume(
            # 指定要持续监听的队列名称，该队列会在 FastAPI 应用启动阶段统一声明和绑定。
            queue=self.settings.rabbitmq_queue,
            # 指定 RabbitMQ 投递一条消息后执行的业务处理函数。
            on_message_callback=self._on_message,
            # 关闭自动确认：只有 _on_message 处理成功后才会显式发送 basic_ack。
            auto_ack=False,
            # 为消费者提供固定标识，便于在 RabbitMQ 管理界面和日志中定位。
            consumer_tag="order-created-consumer",
        )
        # 记录消费者已准备完毕，方便确认其监听的目标队列。
        logger.info("消费者开始监听队列：%s", self.settings.rabbitmq_queue)

        # 开始阻塞式消费循环；该调用会持续接收 RabbitMQ 推送的消息。
        try:
            # 进入消费循环，直到收到停止信号、连接异常，或显式调用 stop_consuming。
            self.channel.start_consuming()
        # 无论消费循环正常结束还是抛出异常，都必须释放 RabbitMQ 连接。
        finally:
            # 安全关闭连接，避免残留 TCP 连接和信道资源。
            close_connection(self.connection)

    def _install_signal_handlers(self) -> None:
        signal.signal(signal.SIGTERM, self._request_stop)
        signal.signal(signal.SIGINT, self._request_stop)

    def _request_stop(self, signum: int, _frame: FrameType | None) -> None:
        logger.info("收到信号 %s，正在停止消费者", signum)
        if self.channel is not None and self.channel.is_open:
            self.channel.stop_consuming()

    def _on_message(
        self,
        channel: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        _properties: pika.BasicProperties,
        body: bytes,
    ) -> None:
        """校验并处理消息，只在成功后发送确认。"""

        try:
            message = MessageEnvelope.model_validate_json(body)
            logger.info(
                "开始处理消息：消息标识=%s，路由键=%s，是否重投递=%s，业务数据=%s",
                message.message_id,
                message.routing_key,
                method.redelivered,
                message.payload,
            )

            if self.settings.consumer_processing_seconds:
                time.sleep(self.settings.consumer_processing_seconds)

            # 示例业务动作通过日志展示。实际应用应在这里执行幂等的业务操作。
        except (ValidationError, ValueError):
            logger.exception("消息格式无效，拒绝消息且不重新入队")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return
        except Exception:
            logger.exception("消息处理失败，拒绝消息且不重新入队")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        channel.basic_ack(delivery_tag=method.delivery_tag)
        logger.info("消息确认完成：消息标识=%s", message.message_id)


def main() -> int:
    """异常退出时返回非零状态码，以便 Supervisor 自动重启。"""

    consumer = OrderCreatedConsumer(get_settings())
    try:
        consumer.run()
    except KeyboardInterrupt:
        logger.info("消费者因键盘中断而停止")
        return 0
    except Exception:
        logger.exception("消费者异常退出")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
