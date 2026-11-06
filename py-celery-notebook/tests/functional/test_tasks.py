import pytest
from pydantic import ValidationError

from src.client.celery_client.celery_publisher import publish_task
from src.model.task_model import MessageTaskPayload
from src.task.async_task import process_message_task


class TestMessageTaskFunctional:
    """验证消息任务的参数校验和业务调用。"""

    def test_task_calls_service_with_valid_payload(self, monkeypatch) -> None:
        """合法参数应转换成模型后调用业务服务。"""

        received: list[MessageTaskPayload] = []
        monkeypatch.setattr(
            "src.task.async_task.process_message",
            lambda payload: received.append(payload),
        )

        task_id = publish_task(
            process_message_task,
            MessageTaskPayload(message="hello"),
        )

        assert task_id
        assert received == [MessageTaskPayload(message="hello")]

    def test_task_rejects_invalid_payload(self, monkeypatch) -> None:
        """参数校验失败时不应调用业务服务。"""

        called = False

        def record_call(_: MessageTaskPayload) -> None:
            nonlocal called
            called = True

        monkeypatch.setattr("src.task.async_task.process_message", record_call)

        with pytest.raises(ValidationError):
            process_message_task.apply(kwargs={"raw_payload": {"message": ""}})

        assert called is False

    def test_task_accepts_maximum_length_payload(self, monkeypatch) -> None:
        """达到模型长度上限的参数仍应进入业务服务。"""

        received: list[MessageTaskPayload] = []
        monkeypatch.setattr(
            "src.task.async_task.process_message",
            lambda payload: received.append(payload),
        )
        payload = MessageTaskPayload(message="x" * 500)

        publish_task(process_message_task, payload)

        assert received == [payload]
