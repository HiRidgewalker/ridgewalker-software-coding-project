"""服务端与测试共用的 JSON-RPC 核心分发器。

这个模块刻意保持逻辑展开，并配上较详细注释。
优先目标是教学清晰度，而不是框架式抽象。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


# Demo 中使用的常见 JSON-RPC 2.0 错误码。
# 这些也是初学者最常接触到的一组标准错误码。
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
# 这是一个自定义业务错误码示例。
# -32099 到 -32000 这段范围通常保留给服务端自定义错误。
USER_NOT_FOUND = -32001


JsonRpcMethod = Callable[[Any], Any]


@dataclass
class JsonRpcError(Exception):
    """可直接转换成 JSON-RPC 错误对象的结构化异常。

    这里把 code/message/data 分开保存，是因为 JSON-RPC 的错误响应
    有固定结构，客户端通常也依赖稳定的数字错误码来处理异常。
    """

    code: int
    message: str
    data: Any = None


class JsonRpcDispatcher:
    """一个很小的 JSON-RPC 2.0 分发器。

    职责包括：
    - 校验传入请求是否符合 JSON-RPC 结构
    - 把方法名路由到已注册的 Python 函数
    - 把函数返回值包装成 JSON-RPC 响应
    - 把执行失败转换成 JSON-RPC 错误对象

    这个类不依赖 HTTP，因此很容易做单元测试，
    后续也可以复用到 WebSocket、stdio 或其他传输层。
    """

    def __init__(self) -> None:
        self.methods: dict[str, JsonRpcMethod] = {}
        self.users = {
            1: {"id": 1, "name": "Alice", "role": "admin"},
            2: {"id": 2, "name": "Bob", "role": "developer"},
            3: {"id": 3, "name": "Carol", "role": "tester"},
        }

        # 启动时就注册好示例方法，这样服务端一运行就可以直接使用。
        self.register("ping", self.ping)
        self.register("add", self.add)
        self.register("get_user", self.get_user)
        self.register("list_methods", self.list_methods)
        self.register("notify_hello", self.notify_hello)

    def register(self, name: str, func: JsonRpcMethod) -> None:
        """把方法名注册到一个 Python 可调用对象上。"""

        self.methods[name] = func

    def dispatch(self, payload: Any) -> dict[str, Any] | list[dict[str, Any]] | None:
        """分发单个请求对象或批量请求。

        返回值含义：
        - dict: 单个 JSON-RPC 响应
        - list[dict]: 批量请求对应的响应列表
        - None: notification，或只包含 notification 的批量请求
        """

        if isinstance(payload, list):
            return self._dispatch_batch(payload)

        return self._dispatch_single(payload)

    def _dispatch_batch(self, payload: list[Any]) -> list[dict[str, Any]] | dict[str, Any] | None:
        """按 JSON-RPC 2.0 规则处理批量请求。"""

        if not payload:
            # 空数组不是合法的批量请求。
            return self.error_response(INVALID_REQUEST, "Invalid Request", request_id=None)

        responses: list[dict[str, Any]] = []
        for item in payload:
            response = self._dispatch_single(item)
            if response is not None:
                responses.append(response)

        # 如果批量请求中的每一项都是 notification，则整体不返回响应。
        return responses or None

    def _dispatch_single(self, request: Any) -> dict[str, Any] | None:
        """处理一个 JSON-RPC 请求对象。"""

        if not isinstance(request, dict):
            return self.error_response(INVALID_REQUEST, "Invalid Request", request_id=None)

        if request.get("jsonrpc") != "2.0":
            return self.error_response(INVALID_REQUEST, "Invalid Request", request_id=request.get("id"))

        method_name = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        is_notification = "id" not in request

        if not isinstance(method_name, str) or not method_name:
            return self.error_response(INVALID_REQUEST, "Invalid Request", request_id=request_id)

        if not isinstance(params, (dict, list)):
            return self.error_response(INVALID_PARAMS, "Invalid params", request_id=request_id)

        method = self.methods.get(method_name)
        if method is None:
            return self.error_response(METHOD_NOT_FOUND, "Method not found", request_id=request_id)

        try:
            result = method(params)
        except JsonRpcError as exc:
            return self.error_response(exc.code, exc.message, request_id=request_id, data=exc.data)
        except Exception as exc:  # noqa: BLE001 - 教学示例里保留清晰的兜底异常分支
            return self.error_response(
                INTERNAL_ERROR,
                "Internal error",
                request_id=request_id,
                data={"details": str(exc)},
            )

        # notification 按协议约定不返回 JSON-RPC 响应体。
        if is_notification:
            return None

        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id,
        }

    def error_response(
        self,
        code: int,
        message: str,
        request_id: Any,
        data: Any = None,
    ) -> dict[str, Any]:
        """构造标准 JSON-RPC 错误响应对象。"""

        error: dict[str, Any] = {
            "code": code,
            "message": message,
        }
        if data is not None:
            error["data"] = data

        return {
            "jsonrpc": "2.0",
            "error": error,
            "id": request_id,
        }

    def ping(self, params: Any) -> str:
        """一个简单的健康检查方法。"""

        self._ensure_object_params("ping", params)
        return "pong"

    def add(self, params: Any) -> int | float:
        """把两个具名参数相加。

        期望参数格式：
        {
            "a": 1,
            "b": 2
        }
        """

        payload = self._ensure_object_params("add", params)
        try:
            a = payload["a"]
            b = payload["b"]
        except KeyError as exc:
            raise JsonRpcError(INVALID_PARAMS, "Invalid params", {"missing": exc.args[0]}) from exc

        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise JsonRpcError(INVALID_PARAMS, "Invalid params", {"reason": "a and b must be numbers"})

        return a + b

    def get_user(self, params: Any) -> dict[str, Any]:
        """根据 id 从内存中的示例数据里返回一个用户。"""

        payload = self._ensure_object_params("get_user", params)
        if "user_id" not in payload:
            raise JsonRpcError(INVALID_PARAMS, "Invalid params", {"missing": "user_id"})

        user_id = payload["user_id"]
        if not isinstance(user_id, int):
            raise JsonRpcError(INVALID_PARAMS, "Invalid params", {"reason": "user_id must be an integer"})

        user = self.users.get(user_id)
        if user is None:
            raise JsonRpcError(USER_NOT_FOUND, "User not found", {"user_id": user_id})

        return user

    def list_methods(self, params: Any) -> list[str]:
        """返回所有已注册方法，方便初学者查看当前服务能力。"""

        self._ensure_object_params("list_methods", params)
        return sorted(self.methods.keys())

    def notify_hello(self, params: Any) -> dict[str, str]:
        """示例 notification 方法。

        这里的 Python 函数仍然返回一个值，因为真正决定是否把结果返回给
        调用方的是分发器。对于 JSON-RPC notification，分发器会主动丢弃响应。
        """

        payload = self._ensure_object_params("notify_hello", params)
        name = payload.get("name", "anonymous")
        return {"message": f"Hello, {name}"}

    def _ensure_object_params(self, method_name: str, params: Any) -> dict[str, Any]:
        """校验方法收到的参数是否为具名对象。

        这个 Demo 选择对象参数，是因为它对初学者来说比位置数组更直观。
        这是示例项目的设计选择，不是协议本身的强制要求。
        """

        if not isinstance(params, dict):
            raise JsonRpcError(
                INVALID_PARAMS,
                "Invalid params",
                {"method": method_name, "reason": "expected object params"},
            )
        return params
