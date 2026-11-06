from google.protobuf.descriptor import FieldDescriptor

import order_service_pb2
import user_service_pb2


TYPE_NAMES = {
    FieldDescriptor.TYPE_STRING: "string",
    FieldDescriptor.TYPE_BOOL: "bool",
    FieldDescriptor.TYPE_INT32: "int32",
    FieldDescriptor.TYPE_INT64: "int64",
    FieldDescriptor.TYPE_MESSAGE: "message",
}


def label_name(field: FieldDescriptor) -> str:
    if field.is_repeated:
        return "repeated"
    return "single"


def field_type_name(field: FieldDescriptor) -> str:
    if field.type == FieldDescriptor.TYPE_MESSAGE:
        return field.message_type.full_name
    return TYPE_NAMES.get(field.type, str(field.type))


def print_descriptor(title: str, message_cls) -> None:
    print(f"== {title} ==")
    descriptor = message_cls.DESCRIPTOR
    for field in descriptor.fields:
        print(
            f"{field.name}: number={field.number}, "
            f"label={label_name(field)}, type={field_type_name(field)}"
        )
    print()


def main() -> None:
    print_descriptor("UserRequest", user_service_pb2.UserRequest)
    print_descriptor("UserReply", user_service_pb2.UserReply)
    print_descriptor("OrderReply", order_service_pb2.OrderReply)

    sample_user = user_service_pb2.UserReply(
        user_id=1001,
        name="Alice",
        age=28,
        active=True,
        tags=["grpc", "python"],
        profile=user_service_pb2.UserReply.Profile(
            email="alice@example.com",
        ),
    )
    print("== Sample UserReply Instance ==")
    print(sample_user)


if __name__ == "__main__":
    main()
