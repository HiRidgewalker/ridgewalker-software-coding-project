"""FastAPI 路由定义。"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException, Request, status

from app.models import (
    HealthResponse,
    MessageEnvelope,
    PublishMessageRequest,
    PublishMessageResponse,
)
from app.rabbitmq import MessageUnroutableError, RabbitMQPublishError, publish_message
from app.settings import Settings

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="查看应用健康状态",
    response_description="应用健康检查结果",
)
async def health(request: Request) -> HealthResponse:
    """返回应用启动阶段确定的拓扑就绪状态。"""

    settings: Settings = request.app.state.settings
    return HealthResponse(
        topology_ready=request.app.state.topology_ready,
        exchange=settings.rabbitmq_exchange,
        queue=settings.rabbitmq_queue,
        binding_key=settings.rabbitmq_binding_key,
    )


@router.post(
    "/messages",
    response_model=PublishMessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="发布消息",
    response_description="RabbitMQ 确认接收消息后的结果",
)
async def create_message(
    payload: PublishMessageRequest,
    request: Request,
) -> PublishMessageResponse:
    """发布持久化消息，不在请求阶段声明 RabbitMQ 拓扑。"""

    settings: Settings = request.app.state.settings
    message = MessageEnvelope(
        routing_key=payload.routing_key,
        payload=payload.payload,
    )

    try:
        await asyncio.to_thread(publish_message, settings, message)
    except MessageUnroutableError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except RabbitMQPublishError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RabbitMQ 当前不可用，消息未被接收。",
        ) from exc

    return PublishMessageResponse(
        message_id=message.message_id,
        routing_key=message.routing_key,
    )
