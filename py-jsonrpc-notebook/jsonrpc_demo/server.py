"""为 JSON-RPC 示例提供 HTTP 传输层。

运行方式：
    python3 -m jsonrpc_demo.server
"""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from jsonrpc_demo.dispatcher import JsonRpcDispatcher, PARSE_ERROR


HOST = "127.0.0.1"
PORT = 8000
RPC_PATH = "/rpc"


# 进程内共享一个分发器实例。
# 这样示例更简单，也方便查看当前注册了哪些方法。
DISPATCHER = JsonRpcDispatcher()


class JsonRpcHandler(BaseHTTPRequestHandler):
    """暴露单个 JSON-RPC 入口的最小 HTTP 处理器。"""

    server_version = "JsonRpcDemo/0.1"

    def do_POST(self) -> None:  # noqa: N802 - 这个方法名由 BaseHTTPRequestHandler 固定要求
        """处理 POST /rpc，并把 HTTP 请求体转换成 JSON-RPC 调用。"""

        if self.path != RPC_PATH:
            self.send_error(HTTPStatus.NOT_FOUND, "Only /rpc is available in this demo")
            return

        try:
            body = self._read_json_body()
        except json.JSONDecodeError:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                DISPATCHER.error_response(PARSE_ERROR, "Parse error", request_id=None),
            )
            return

        response_payload = DISPATCHER.dispatch(body)

        # notification 按协议不返回 JSON-RPC 响应体。
        if response_payload is None:
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()
            return

        self._send_json(HTTPStatus.OK, response_payload)

    def do_GET(self) -> None:  # noqa: N802 - 这个方法名由 BaseHTTPRequestHandler 固定要求
        """给直接用浏览器访问的学习者返回一段简短提示文本。"""

        if self.path == "/":
            message = (
                "JSON-RPC demo server is running.\n"
                f"Send POST requests to {RPC_PATH} with a JSON-RPC 2.0 body.\n"
            )
            encoded = message.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Use GET / or POST /rpc")

    def log_message(self, format: str, *args: object) -> None:
        """让日志保持简洁，但对本地学习仍然有帮助。"""

        print(f"[server] {self.address_string()} - {format % args}")

    def _read_json_body(self) -> object:
        """读取请求体并把它解码为 JSON。"""

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)
        return json.loads(raw_body.decode("utf-8"))

    def _send_json(self, status: HTTPStatus, payload: object) -> None:
        """把 Python 数据序列化成 JSON，并写入 HTTP 响应。"""

        encoded = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def run_server(host: str = HOST, port: int = PORT) -> None:
    """启动多线程 HTTP 服务，并持续阻塞运行。"""

    server = ThreadingHTTPServer((host, port), JsonRpcHandler)
    print(f"JSON-RPC server listening on http://{host}:{port}{RPC_PATH}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
