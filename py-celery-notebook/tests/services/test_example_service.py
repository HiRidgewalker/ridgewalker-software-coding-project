import logging

from src.model.task_model import MessageTaskPayload
from src.service.example_service import process_message


class TestExampleService:
    """验证示例业务服务的可观察行为。"""

    def test_process_message_logs_message_length(self, caplog) -> None:
        """处理消息时应记录消息长度且不记录原文。"""

        payload = MessageTaskPayload(message="hello")

        with caplog.at_level(logging.INFO):
            process_message(payload)

        assert "message_length=5" in caplog.text
        assert "hello" not in caplog.text

    def test_process_message_logs_maximum_length(self, caplog) -> None:
        """达到参数上限的消息仍应被正常处理。"""

        payload = MessageTaskPayload(message="x" * 500)

        with caplog.at_level(logging.INFO):
            process_message(payload)

        assert "message_length=500" in caplog.text
