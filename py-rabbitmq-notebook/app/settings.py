"""接口服务、拓扑初始化器和消费者共用的配置。"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

import pika
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """固定单消费者学习拓扑的配置。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    rabbitmq_host: str = "127.0.0.1"
    rabbitmq_port: int = Field(default=5672, ge=1, le=65535)
    rabbitmq_user: str = "admin"
    rabbitmq_password: str = "admin"
    rabbitmq_vhost: str = "/"
    rabbitmq_exchange: str = "orders.direct"
    rabbitmq_exchange_type: Literal["direct"] = "direct"
    rabbitmq_queue: str = "orders.created.queue"
    rabbitmq_binding_key: str = "order.created"
    topology_initialization_attempts: int = Field(default=10, ge=1, le=60)
    topology_initialization_retry_seconds: float = Field(default=1.0, gt=0, le=30)
    consumer_processing_seconds: float = Field(default=0.0, ge=0, le=60)

    @property
    def connection_parameters(self) -> pika.ConnectionParameters:
        """为当前操作构造新的 Pika 连接配置。"""

        credentials = pika.PlainCredentials(
            username=self.rabbitmq_user,
            password=self.rabbitmq_password,
        )
        return pika.ConnectionParameters(
            host=self.rabbitmq_host,
            port=self.rabbitmq_port,
            virtual_host=self.rabbitmq_vhost,
            credentials=credentials,
            heartbeat=30,
            blocked_connection_timeout=10,
        )


@lru_cache
def get_settings() -> Settings:
    """返回每个进程唯一的不可变配置对象。"""

    return Settings()
