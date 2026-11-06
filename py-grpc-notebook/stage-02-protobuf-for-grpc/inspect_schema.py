import user_pb2
import user_pb2_grpc


def main() -> None:
    request = user_pb2.UserRequest(user_id=101, include_tags=True)
    reply = user_pb2.UserReply(
        user_id=101,
        name="Alice",
        age=28,
        active=True,
        tags=["grpc", "protobuf", "python"],
    )

    print("request message:")
    print(request)
    print()

    print("reply message:")
    print(reply)
    print()

    print("generated gRPC classes:")
    print(f"- stub: {user_pb2_grpc.UserServiceStub.__name__}")
    print(f"- servicer: {user_pb2_grpc.UserServiceServicer.__name__}")


if __name__ == "__main__":
    main()
