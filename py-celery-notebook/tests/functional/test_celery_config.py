from datetime import timedelta

import pytest
from kombu import Connection
from pydantic import ValidationError

from src.client.celery_client.celery_config import (
    ASYNC_QUEUE_NAME,
    BEAT_SCHEDULE,
    HEARTBEAT_TASK_NAME,
    SCHEDULED_QUEUE_NAME,
    TASK_IMPORTS,
    TASK_QUEUES,
    TASK_ROUTES,
    CelerySettings,
    celery_app,
)


class TestCeleryConfigFunctional:
    """验证集中配置的连接、路由和调度约束。"""

    def test_broker_url_escapes_credentials_and_vhost(self) -> None:
        """broker URL 应正确转义凭据和 vhost。"""

        settings = CelerySettings(
            rabbitmq_user="user@example.com",
            rabbitmq_password="p@ss/word",
            rabbitmq_vhost="team/tasks",
        )

        assert settings.broker_url == (
            "amqp://user%40example.com:p%40ss%2Fword@127.0.0.1:5672/team%2Ftasks"
        )
        assert Connection(settings.broker_url).virtual_host == "team/tasks"

    def test_settings_reject_invalid_port(self) -> None:
        """端口超出合法范围时应在配置加载阶段失败。"""

        with pytest.raises(ValidationError):
            CelerySettings(
                rabbitmq_user="user",
                rabbitmq_password="password",
                rabbitmq_port=0,
            )

    def test_settings_accept_maximum_port(self) -> None:
        """最大合法端口应被接受。"""

        settings = CelerySettings(
            rabbitmq_user="user",
            rabbitmq_password="password",
            rabbitmq_port=65535,
        )

        assert settings.rabbitmq_port == 65535

    def test_routes_and_schedule_use_declared_queues(self) -> None:
        """路由和 Beat 计划只能指向已声明队列。"""

        queue_names = {queue.name for queue in TASK_QUEUES}
        route_queues = {route["queue"] for route in TASK_ROUTES.values()}

        assert queue_names == {ASYNC_QUEUE_NAME, SCHEDULED_QUEUE_NAME}
        assert route_queues <= queue_names
        assert BEAT_SCHEDULE["example-heartbeat-every-five-seconds"]["task"] == (
            HEARTBEAT_TASK_NAME
        )
        assert celery_app.conf.task_create_missing_queues is False

    def test_heartbeat_schedule_runs_every_five_seconds(self) -> None:
        """心跳计划应使用 Celery 支持的五秒间隔。"""

        schedule = BEAT_SCHEDULE["example-heartbeat-every-five-seconds"]["schedule"]

        assert schedule == timedelta(seconds=5)

    def test_task_imports_use_src_modules(self) -> None:
        """Worker 应只从迁移后的 src 模块导入任务。"""

        assert TASK_IMPORTS == (
            "src.task.async_task",
            "src.task.scheduled_task",
        )
