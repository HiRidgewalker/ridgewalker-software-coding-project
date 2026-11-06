import asyncio

from fastapi import APIRouter, status

from src.client.celery_client.celery_publisher import publish_task
from src.model.task_model import MessageTaskPayload, TaskAcceptedResponse
from src.task.async_task import process_message_task

router = APIRouter()


@router.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    """返回应用健康状态。"""

    return {"status": "ok"}


@router.post(
    "/tasks/messages",
    response_model=TaskAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["tasks"],
)
async def enqueue_message(payload: MessageTaskPayload) -> TaskAcceptedResponse:
    """发布消息处理任务并返回任务标识。"""

    task_id = await asyncio.to_thread(publish_task, process_message_task, payload)
    return TaskAcceptedResponse(task_id=task_id)
