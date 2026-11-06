from concurrent import futures
import time

import grpc

import common_pb2
import order_service_pb2
import order_service_pb2_grpc
import user_service_pb2
import user_service_pb2_grpc


USERS = {
    1001: {
        "name": "Alice",
        "age": 28,
        "active": True,
        "tags": ["grpc", "python"],
        "email": "alice@example.com",
        "city": "Shanghai",
        "country": "China",
    },
    1002: {
        "name": "Bob",
        "age": 31,
        "active": False,
        "tags": ["backend", "protobuf"],
        "email": "bob@example.com",
        "city": "Hangzhou",
        "country": "China",
    },
}

ORDERS = {
    "ord-100": {
        "user_id": 1001,
        "paid": True,
        "items": [
            {"sku": "book-grpc", "quantity": 1, "currency": "CNY", "units": 88},
            {"sku": "course-proto", "quantity": 2, "currency": "CNY", "units": 199},
        ],
    }
}


def build_user_reply(user_id: int, include_tags: bool) -> user_service_pb2.UserReply:
    user = USERS[user_id]
    tags = user["tags"] if include_tags else []

    return user_service_pb2.UserReply(
        user_id=user_id,
        name=user["name"],
        age=user["age"],
        active=user["active"],
        tags=tags,
        profile=user_service_pb2.UserReply.Profile(
            email=user["email"],
            address=common_pb2.Address(city=user["city"], country=user["country"]),
        ),
    )


class UserService(user_service_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        request_id = dict(context.invocation_metadata()).get("x-request-id", "missing")
        context.set_trailing_metadata(
            (("x-request-id", request_id), ("served-by", "stage4-user-service"))
        )

        if request.user_id <= 0:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "user_id must be positive")

        if request.user_id not in USERS:
            context.abort(grpc.StatusCode.NOT_FOUND, f"user {request.user_id} not found")

        return build_user_reply(request.user_id, request.include_tags)

    def SearchUsers(self, request, context):
        if request.limit <= 0:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "limit must be positive")

        # Small artificial delay to demonstrate client-side deadline handling.
        if request.keyword == "slow":
            time.sleep(1.0)

        keyword = request.keyword.lower()
        matched_users = []

        for user_id, user in USERS.items():
            if keyword and keyword not in user["name"].lower() and keyword not in " ".join(
                user["tags"]
            ).lower():
                continue
            matched_users.append(build_user_reply(user_id, include_tags=True))
            if len(matched_users) >= request.limit:
                break

        return user_service_pb2.SearchUsersReply(users=matched_users)


class OrderService(order_service_pb2_grpc.OrderServiceServicer):
    def GetOrder(self, request, context):
        if not request.order_id:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "order_id is required")

        if request.order_id not in ORDERS:
            context.abort(grpc.StatusCode.NOT_FOUND, f"order {request.order_id} not found")

        order = ORDERS[request.order_id]
        items = [
            order_service_pb2.OrderReply.Item(
                sku=item["sku"],
                quantity=item["quantity"],
                unit_price=common_pb2.Money(
                    currency=item["currency"],
                    units=item["units"],
                ),
            )
            for item in order["items"]
        ]

        return order_service_pb2.OrderReply(
            order_id=request.order_id,
            user_id=order["user_id"],
            paid=order["paid"],
            items=items,
        )


def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_service_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    order_service_pb2_grpc.add_OrderServiceServicer_to_server(OrderService(), server)
    server.add_insecure_port("0.0.0.0:50053")
    server.start()
    print("server started at 0.0.0.0:50053")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()

