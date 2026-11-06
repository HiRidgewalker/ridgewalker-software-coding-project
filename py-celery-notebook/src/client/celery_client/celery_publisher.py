from celery import Task
from pydantic import BaseModel


def publish_task(task: Task, payload: BaseModel) -> str:
    """按统一的 raw_payload 参数约定发布异步任务。"""

    result = task.apply_async(
        kwargs={"raw_payload": payload.model_dump(mode="json")},
    )
    return str(result.id)
