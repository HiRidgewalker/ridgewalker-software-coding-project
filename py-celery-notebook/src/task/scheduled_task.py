import logging
from datetime import UTC, datetime

from src.client.celery_client.celery_config import HEARTBEAT_TASK_NAME, celery_app
from src.service.example_service import record_heartbeat
from src.task.base_task import LoggedTask

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    base=LoggedTask,
    name=HEARTBEAT_TASK_NAME,
    acks_late=True,
)
def heartbeat_task(self: LoggedTask) -> None:
    """记录周期心跳任务的执行时间。"""

    executed_at = datetime.now(UTC)
    logger.info(f"任务开始：任务名称={self.name}，任务标识={self.request.id}")
    record_heartbeat(executed_at)
