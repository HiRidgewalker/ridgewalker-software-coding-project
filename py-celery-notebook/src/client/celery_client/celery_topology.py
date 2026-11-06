import logging

from src.client.celery_client.celery_config import TASK_QUEUES, celery_app

logger = logging.getLogger(__name__)


def declare_topology() -> None:
    """向 RabbitMQ 声明集中配置的交换机、队列和绑定。"""

    with celery_app.connection_for_write() as connection:
        connection.ensure_connection(max_retries=3)
        channel = connection.channel()
        try:
            for queue in TASK_QUEUES:
                queue(channel).declare()
                logger.info(f"RabbitMQ 队列已就绪：queue={queue.name}")
        finally:
            channel.close()


def main() -> None:
    """初始化日志并声明 RabbitMQ 拓扑。"""

    logging.basicConfig(level=logging.INFO)
    declare_topology()


if __name__ == "__main__":
    main()
