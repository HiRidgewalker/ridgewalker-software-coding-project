import logging
from typing import Any

from celery import Task

logger = logging.getLogger(__name__)


class LoggedTask(Task):
    """统一记录 Celery Task 的成功、重试和失败事件。"""

    abstract = True

    def on_success(
        self,
        retval: Any,
        task_id: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> None:
        """记录任务成功事件。"""

        logger.info(f"任务执行成功：任务名称={self.name}，任务标识={task_id}")
        super().on_success(retval, task_id, args, kwargs)

    def on_retry(
        self,
        exc: BaseException,
        task_id: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        einfo: Any,
    ) -> None:
        """记录任务重试事件。"""

        logger.exception(
            f"任务准备重试：任务名称={self.name}，任务标识={task_id}，"
            f"重试次数={self.request.retries}，原因={exc}"
        )
        super().on_retry(exc, task_id, args, kwargs, einfo)

    def on_failure(
        self,
        exc: BaseException,
        task_id: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        einfo: Any,
    ) -> None:
        """记录任务失败事件。"""

        logger.exception(
            f"任务执行失败：任务名称={self.name}，任务标识={task_id}，原因={exc}"
        )
        super().on_failure(exc, task_id, args, kwargs, einfo)
