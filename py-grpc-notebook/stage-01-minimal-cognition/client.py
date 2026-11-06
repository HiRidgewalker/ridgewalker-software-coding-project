import grpc

import hello_pb2
import hello_pb2_grpc


def run() -> None:
    channel_options = [("grpc.enable_http_proxy", 0)]

    with grpc.insecure_channel("127.0.0.1:50051", options=channel_options) as channel:
        stub = hello_pb2_grpc.GreeterStub(channel)
        response = stub.SayHello(hello_pb2.HelloRequest(name="grpc learner"))
    print(f"response from server: {response.message}")


if __name__ == "__main__":
    run()
