import grpc

import user_service_pb2
import user_service_pb2_grpc


def run() -> None:
    channel_options = [("grpc.enable_http_proxy", 0)]

    with grpc.insecure_channel("127.0.0.1:50052", options=channel_options) as channel:
        stub = user_service_pb2_grpc.UserServiceStub(channel)
        request = user_service_pb2.UserRequest(user_id=1001)
        response = stub.GetUser(request)

    print(f"response.user_id = {response.user_id}")
    print(f"response.name = {response.name}")
    print(f"response.active = {response.active}")


if __name__ == "__main__":
    run()
