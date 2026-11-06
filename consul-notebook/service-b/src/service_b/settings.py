from functools import lru_cache
from pathlib import Path
from typing import Self

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """从 service-b/.env 加载服务配置。"""

    model_config = SettingsConfigDict(
        env_file=PROJECT_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        frozen=True,
    )

    consul_http_addr: str
    consul_token: str | None = None
    service_name: str
    service_id: str
    peer_service_name: str
    consul_health_interval_seconds: int = Field(gt=0)
    consul_health_timeout_seconds: int = Field(gt=0)
    consul_deregister_after_seconds: int = Field(gt=0)
    http_timeout_seconds: float = Field(gt=0)

    @field_validator("consul_http_addr")
    @classmethod
    def normalize_consul_address(cls, value: str) -> str:
        """移除末尾斜杠，并校验 Consul 地址使用 HTTP(S) 协议。"""
        value = value.rstrip("/")
        if not value.startswith(("http://", "https://")):
            raise ValueError("CONSUL_HTTP_ADDR 必须以 http:// 或 https:// 开头")
        return value

    @model_validator(mode="after")
    def validate_health_check_intervals(self) -> Self:
        """确保主动检查超时时间小于检查间隔。"""
        if (
            self.consul_health_timeout_seconds
            >= self.consul_health_interval_seconds
        ):
            raise ValueError(
                "CONSUL_HEALTH_TIMEOUT_SECONDS 必须小于 "
                "CONSUL_HEALTH_INTERVAL_SECONDS"
            )
        return self

    @property
    def consul_check_id(self) -> str:
        """返回 Consul 为当前服务实例创建的健康检查 ID。"""
        return f"service:{self.service_id}"


@lru_cache
def get_settings() -> Settings:
    """从 service-b/.env 加载并缓存配置。"""
    return Settings()  # type: ignore[call-arg]
