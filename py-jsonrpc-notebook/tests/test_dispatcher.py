"""JSON-RPC 分发器的单元测试。

这些测试主要关注协议处理逻辑，因为这是初学者最应该先看懂的部分。
"""

from __future__ import annotations  # 延迟解析类型注解，便于前向引用

import unittest

from jsonrpc_demo.dispatcher import (
    INVALID_PARAMS,
    INVALID_REQUEST,
    METHOD_NOT_FOUND,
    JsonRpcDispatcher,
)


class JsonRpcDispatcherTestCase(unittest.TestCase):
    """覆盖分发器主要成功与失败分支的测试集合。"""

    def setUp(self) -> None:
        self.dispatcher = JsonRpcDispatcher()

    def test_ping_success(self) -> None:
        response = self.dispatcher.dispatch(
            {
                "jsonrpc": "2.0",
                "method": "ping",
                "params": {},
                "id": 1,
            }
        )

        self.assertEqual(
            response,
            {
                "jsonrpc": "2.0",
                "result": "pong",
                "id": 1,
            },
        )

    def test_method_not_found(self) -> None:
        response = self.dispatcher.dispatch(
            {
                "jsonrpc": "2.0",
                "method": "missing_method",
                "params": {},
                "id": 2,
            }
        )

        assert isinstance(response, dict)
        self.assertEqual(response["error"]["code"], METHOD_NOT_FOUND)

    def test_invalid_request_when_jsonrpc_version_is_missing(self) -> None:
        response = self.dispatcher.dispatch(
            {
                "method": "ping",
                "params": {},
                "id": 3,
            }
        )

        assert isinstance(response, dict)
        self.assertEqual(response["error"]["code"], INVALID_REQUEST)

    def test_invalid_params_for_add(self) -> None:
        response = self.dispatcher.dispatch(
            {
                "jsonrpc": "2.0",
                "method": "add",
                "params": {"a": "wrong", "b": 1},
                "id": 4,
            }
        )

        assert isinstance(response, dict)
        self.assertEqual(response["error"]["code"], INVALID_PARAMS)

    def test_notification_returns_none(self) -> None:
        response = self.dispatcher.dispatch(
            {
                "jsonrpc": "2.0",
                "method": "notify_hello",
                "params": {"name": "Alice"},
            }
        )

        self.assertIsNone(response)

    def test_batch_request_skips_notification_response(self) -> None:
        response = self.dispatcher.dispatch(
            [
                {
                    "jsonrpc": "2.0",
                    "method": "ping",
                    "params": {},
                    "id": 10,
                },
                {
                    "jsonrpc": "2.0",
                    "method": "notify_hello",
                    "params": {"name": "Alice"},
                },
                {
                    "jsonrpc": "2.0",
                    "method": "add",
                    "params": {"a": 2, "b": 3},
                    "id": 11,
                },
            ]
        )

        assert isinstance(response, list)
        self.assertEqual(
            response,
            [
                {"jsonrpc": "2.0", "result": "pong", "id": 10},
                {"jsonrpc": "2.0", "result": 5, "id": 11},
            ],
        )

    def test_empty_batch_is_invalid_request(self) -> None:
        response = self.dispatcher.dispatch([])

        assert isinstance(response, dict)
        self.assertEqual(response["error"]["code"], INVALID_REQUEST)


if __name__ == "__main__":
    unittest.main()
