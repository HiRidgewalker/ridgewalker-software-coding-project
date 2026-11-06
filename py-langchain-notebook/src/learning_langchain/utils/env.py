from __future__ import annotations

from textwrap import dedent


def missing_env_message() -> str:
    return dedent(
        """
        Missing required environment variables.
        Set OPENAI_API_KEY before running examples.
        Optional:
        - OPENAI_MODEL
        - OPENAI_BASE_URL
        """
    ).strip()
