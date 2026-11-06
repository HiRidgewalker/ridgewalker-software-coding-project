from __future__ import annotations

from langchain_openai import ChatOpenAI

from learning_langchain.config import load_config


def build_chat_model(*, temperature: float = 0) -> ChatOpenAI:
    config = load_config()
    return ChatOpenAI(
        model=config.openai_model,
        api_key=config.openai_api_key,
        base_url=config.openai_base_url,
        temperature=temperature,
    )
