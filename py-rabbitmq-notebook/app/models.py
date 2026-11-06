"""Pydantic 请求、响应和消息信封模型。"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

RoutingKey = Annotated[
    str,
    Field(
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9._-]+$",
        description="直连交换机使用的路由键，例如 order.created。",
    ),
]


class PublishMessageRequest(BaseModel):
    """生产者接口接收并校验的请求。"""

    model_config = ConfigDict(extra="forbid", title="发布消息请求")

    routing_key: RoutingKey
    payload: dict[str, Any] = Field(
        min_length=1,
        description="待发送的业务数据，必须是非空 JSON 对象。",
    )


class MessageEnvelope(BaseModel):
    """存储在 RabbitMQ 中的 JSON 消息。"""

    model_config = ConfigDict(title="消息信封")

    message_id: UUID = Field(default_factory=uuid4)
    routing_key: RoutingKey
    published_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any]


class PublishMessageResponse(BaseModel):
    """RabbitMQ 确认发布后返回的响应。"""

    model_config = ConfigDict(title="发布消息响应")

    message_id: UUID
    routing_key: RoutingKey
    status: Literal["published"] = "published"


class HealthResponse(BaseModel):
    """FastAPI 启动阶段确定的就绪状态。"""

    model_config = ConfigDict(title="健康检查响应")

    status: Literal["ok"] = "ok"
    topology_ready: bool
    exchange: str
    queue: str
    binding_key: str
