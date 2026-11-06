from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MessageTaskPayload(BaseModel):
    """消息异步任务的输入参数。"""

    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1, max_length=500)


class TaskAcceptedResponse(BaseModel):
    """任务成功发布后的 HTTP 响应。"""

    task_id: UUID
    status: Literal["已入队"] = "已入队"
