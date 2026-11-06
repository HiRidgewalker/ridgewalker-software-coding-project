from __future__ import annotations

import os
from dataclasses import dataclass


# dataclass 自动生成初始化等样板代码；slots=True 限制实例字段并减少开销。
@dataclass(slots=True)
class AppConfig:
    openai_api_key: str
    openai_model: str = "gpt-4.1-mini"
    openai_base_url: str | None = None

    def __post_init__(self) -> None:
        if not self.openai_api_key.strip():
            raise ValueError("OPENAI_API_KEY must not be blank")


def load_config() -> AppConfig:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required to run the examples")

    model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini").strip() or "gpt-4.1-mini"
    base_url = os.environ.get("OPENAI_BASE_URL", "").strip() or None

    return AppConfig(
        openai_api_key=api_key,
        openai_model=model,
        openai_base_url=base_url,
    )
