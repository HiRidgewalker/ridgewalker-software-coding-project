"""演示如何调用示例服务端的小型客户端脚本。

请在启动服务端后运行：
    python3 -m jsonrpc_demo.client
"""

from __future__ import annotations

import json
from urllib import request
from urllib.error import HTTPError, URLError


SERVER_URL = "http://127.0.0.1:8000/rpc"


def send_jsonrpc(payload: object) -> tuple[int, str]:
    """发送一个 JSON-RPC 请求，并返回 HTTP 状态码和响应体。"""

    data = json.dumps(payload).encode("utf-8")
    http_request = request.Request(
        SERVER_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(http_request) as response:
            return response.status, response.read().decode("utf-8")
    except HTTPError as exc:
        return exc.code, exc.read().decode("utf-8")
    except URLError as exc:
        raise SystemExit(
            "Could not connect to the demo server. "
            "Start it first with: python3 -m jsonrpc_demo.server\n"
            f"Details: {exc}"
        ) from exc


def print_example(title: str, payload: object) -> None:
    """为学习者格式化打印一组请求与响应示例。"""

    print(f"\n=== {title} ===")
    print("Request:")
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    status, response_text = send_jsonrpc(payload)
    print(f"HTTP status: {status}")
    if response_text:
        print("Response:")
        print(response_text)
    else:
        print("Response: <empty body>")


def main() -> None:
    """依次运行一组覆盖主要 JSON-RPC 场景的示例。"""

    print_example(
        "Basic call: ping",
        {
            "jsonrpc": "2.0",
            "method": "ping",
            "params": {},
            "id": 1,
        },
    )

    print_example(
        "Method with parameters: add",
        {
            "jsonrpc": "2.0",
            "method": "add",
            "params": {"a": 7, "b": 5},
            "id": 2,
        },
    )

    print_example(
        "Query in-memory demo data: get_user",
        {
            "jsonrpc": "2.0",
            "method": "get_user",
            "params": {"user_id": 1},
            "id": 3,
        },
    )

    print_example(
        "Error example: unknown method",
        {
            "jsonrpc": "2.0",
            "method": "unknown_method",
            "params": {},
            "id": 4,
        },
    )

    print_example(
        "Notification example: no id means no JSON-RPC response",
        {
            "jsonrpc": "2.0",
            "method": "notify_hello",
            "params": {"name": "Alice"},
        },
    )

    print_example(
        "Batch example",
        [
            {
                "jsonrpc": "2.0",
                "method": "ping",
                "params": {},
                "id": 10,
            },
            {
                "jsonrpc": "2.0",
                "method": "add",
                "params": {"a": 10, "b": 20},
                "id": 11,
            },
            {
                "jsonrpc": "2.0",
                "method": "notify_hello",
                "params": {"name": "Batch user"},
            },
        ],
    )


if __name__ == "__main__":
    main()
