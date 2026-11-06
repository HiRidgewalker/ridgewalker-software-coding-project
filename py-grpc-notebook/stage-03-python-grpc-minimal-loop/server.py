from concurrent import futures

import grpc

import user_service_pb2
import user_service_pb2_grpc


class UserService(user_service_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        return user_service_pb2.UserReply(
            user_id=request.user_id,
            name="Alice",
            active=True,
        )


def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_service_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port("0.0.0.0:50052")
    server.start()
    print("server started at 0.0.0.0:50052")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()

