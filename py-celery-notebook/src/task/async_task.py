import logging

from src.client.celery_client.celery_config import PROCESS_MESSAGE_TASK_NAME, celery_app
from src.core.exception import RetryableTaskError
from src.model.task_model import MessageTaskPayload
from src.service.example_service import process_message
from src.task.base_task import LoggedTask

logger = logging.getLogger(__name__)

RETRY_BACKOFF_MAX_SECONDS = 600
MAX_RETRY_COUNT = 5


@celery_app.task(
    bind=True,
    base=LoggedTask,
    name=PROCESS_MESSAGE_TASK_NAME,
    autoretry_for=(RetryableTaskError,),
    retry_backoff=True,
    retry_backoff_max=RETRY_BACKOFF_MAX_SECONDS,
    retry_jitter=True,
    max_retries=MAX_RETRY_COUNT,
    acks_late=True,
)
def process_message_task(self: LoggedTask, raw_payload: dict[str, object]) -> None:
    """校验消息参数并调用普通业务服务。"""

    logger.info(f"=== {raw_payload} ===")
    payload = MessageTaskPayload.model_validate(raw_payload)
    logger.info(f"任务开始：任务名称={self.name}，任务标识={self.request.id}")
    process_message(payload)
