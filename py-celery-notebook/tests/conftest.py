import os
from collections.abc import Iterator

import pytest

os.environ.setdefault("RABBITMQ_USER", "test-user")
os.environ.setdefault("RABBITMQ_PASSWORD", "test-password")

from src.client.celery_client.celery_config import celery_app  # noqa: E402


@pytest.fixture(autouse=True)
def eager_celery() -> Iterator[None]:
    """让测试中的 Celery Task 在当前进程执行。"""

    previous_eager = celery_app.conf.task_always_eager
    previous_propagates = celery_app.conf.task_eager_propagates
    celery_app.conf.update(task_always_eager=True, task_eager_propagates=True)
    yield
    celery_app.conf.update(
        task_always_eager=previous_eager,
        task_eager_propagates=previous_propagates,
    )
