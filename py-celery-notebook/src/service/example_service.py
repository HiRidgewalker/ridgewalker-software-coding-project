import logging
from datetime import datetime

from src.model.task_model import MessageTaskPayload

logger = logging.getLogger(__name__)


def process_message(payload: MessageTaskPayload) -> None:
    """处理异步任务收到的消息。"""

    logger.info(f"业务函数处理消息：message_length={len(payload.message)}")


def record_heartbeat(executed_at: datetime) -> None:
    """记录周期任务的执行时间。"""

    logger.info(f"周期心跳：executed_at={executed_at.isoformat()}")
