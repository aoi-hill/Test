import redis
from google.protobuf import descriptor_pb2, descriptor_pool, message_factory

# ----------------------
# Redis Setup
# ----------------------
redis_client = redis.Redis(host='localhost', port=6379, db=0)
SCHEMA_HASH = "schemas"
STREAM_KEY = "messages"

# ----------------------
# Producer
# ----------------------
def producer():
    # 1. Dynamically define schema
    fd_proto = descriptor_pb2.FileDescriptorProto()
    fd_proto.name = "person.proto"
    fd_proto.package = "tutorial"

    msg_proto = fd_proto.message_type.add()
    msg_proto.name = "Person"

    # Add fields
    f_name = msg_proto.field.add()
    f_name.name = "name"
    f_name.number = 1
    f_name.label = descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
    f_name.type = descriptor_pb2.FieldDescriptorProto.TYPE_STRING

    f_age = msg_proto.field.add()
    f_age.name = "age"
    f_age.number = 2
    f_age.label = descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
    f_age.type = descriptor_pb2.FieldDescriptorProto.TYPE_INT32

    schema_id = "person_v1"

    # 2. Push schema to Redis if not exists
    if not redis_client.hexists(SCHEMA_HASH, schema_id):
        redis_client.hset(SCHEMA_HASH, schema_id, fd_proto.SerializeToString())

    # 3. Register schema in local pool and create dynamic message
    pool = descriptor_pool.DescriptorPool()
    pool.Add(fd_proto)
    person_desc = pool.FindMessageTypeByName("tutorial.Person")
    factory = message_factory.MessageFactory(pool)
    PersonClass = factory.GetPrototype(person_desc)

    # 4. Create message
    person_msg = PersonClass()
    person_msg.name = "Alice"
    person_msg.age = 30

    # 5. Serialize message
    payload = person_msg.SerializeToString()

    # 6. Push to Redis Stream
    redis_client.xadd(STREAM_KEY, {"schema_id": schema_id, "payload": payload})
    print("Producer: Message sent.")


# ----------------------
# Consumer
# ----------------------
def consumer():
    # 1. Read message from Redis Stream
    entries = redis_client.xread({STREAM_KEY: '0-0'}, count=1, block=1000)
    for stream_name, messages in entries:
        for message_id, message_data in messages:
            schema_id = message_data[b"schema_id"].decode()
            payload = message_data[b"payload"]

            # 2. Fetch schema from Redis if not in local pool
            pool = descriptor_pool.DescriptorPool()
            if True:  # For simplicity, always fetch from Redis
                schema_bytes = redis_client.hget(SCHEMA_HASH, schema_id)
                fd_proto = descriptor_pb2.FileDescriptorProto()
                fd_proto.ParseFromString(schema_bytes)
                pool.Add(fd_proto)

            # 3. Create dynamic message class
            person_desc = pool.FindMessageTypeByName("tutorial.Person")
            factory = message_factory.MessageFactory(pool)
            PersonClass = factory.GetPrototype(person_desc)

            # 4. Deserialize
            person_msg = PersonClass()
            person_msg.ParseFromString(payload)

            print(f"Consumer: Received message -> name: {person_msg.name}, age: {person_msg.age}")


if __name__ == "__main__":
    producer()
    consumer()
