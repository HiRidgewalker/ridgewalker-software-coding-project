import grpc

import order_service_pb2
import order_service_pb2_grpc
import user_service_pb2
import user_service_pb2_grpc


CHANNEL_OPTIONS = [("grpc.enable_http_proxy", 0)]
METADATA = (("x-request-id", "stage4-request-001"), ("client-name", "stage4-demo"))


def demo_get_user(channel: grpc.Channel) -> None:
    print("== GetUser ==")
    stub = user_service_pb2_grpc.UserServiceStub(channel)
    request = user_service_pb2.UserRequest(user_id=1001, include_tags=True)
    response, call = stub.GetUser.with_call(request, metadata=METADATA, timeout=2.0)

    print(f"user_id = {response.user_id}")
    print(f"name = {response.name}")
    print(f"age = {response.age}")
    print(f"active = {response.active}")
    print(f"tags = {list(response.tags)}")
    print(f"profile.email = {response.profile.email}")
    print(f"profile.address.city = {response.profile.address.city}")
    print(f"trailing metadata = {dict(call.trailing_metadata())}")
    print()


def demo_search_users(channel: grpc.Channel) -> None:
    print("== SearchUsers ==")
    stub = user_service_pb2_grpc.UserServiceStub(channel)
    request = user_service_pb2.SearchUsersRequest(keyword="grpc", limit=10)
    response = stub.SearchUsers(request, timeout=2.0)

    for user in response.users:
        print(f"user {user.user_id}: {user.name}, tags={list(user.tags)}")
    print()


def demo_get_order(channel: grpc.Channel) -> None:
    print("== GetOrder ==")
    stub = order_service_pb2_grpc.OrderServiceStub(channel)
    request = order_service_pb2.OrderRequest(order_id="ord-100")
    response = stub.GetOrder(request, timeout=2.0)

    print(f"order_id = {response.order_id}")
    print(f"user_id = {response.user_id}")
    print(f"paid = {response.paid}")
    for item in response.items:
        print(
            f"item sku={item.sku}, quantity={item.quantity}, "
            f"unit_price={item.unit_price.currency} {item.unit_price.units}"
        )
    print()


def demo_error(channel: grpc.Channel) -> None:
    print("== Error Handling ==")
    stub = user_service_pb2_grpc.UserServiceStub(channel)

    try:
        stub.GetUser(user_service_pb2.UserRequest(user_id=9999), timeout=2.0)
    except grpc.RpcError as exc:
        print(f"code = {exc.code().name}")
        print(f"details = {exc.details()}")
    print()


def demo_timeout(channel: grpc.Channel) -> None:
    print("== Timeout ==")
    stub = user_service_pb2_grpc.UserServiceStub(channel)

    try:
        stub.SearchUsers(
            user_service_pb2.SearchUsersRequest(keyword="slow", limit=1),
            timeout=0.2,
        )
    except grpc.RpcError as exc:
        print(f"code = {exc.code().name}")
        print(f"details = {exc.details()}")
    print()


def main() -> None:
    with grpc.insecure_channel("127.0.0.1:50053", options=CHANNEL_OPTIONS) as channel:
        demo_get_user(channel)
        demo_search_users(channel)
        demo_get_order(channel)
        demo_error(channel)
        demo_timeout(channel)


if __name__ == "__main__":
    main()

