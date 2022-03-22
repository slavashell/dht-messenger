from fastapi import FastAPI
from pydantic import BaseModel

from dht_node.dht_node import DHTNode
from client import ConnectionManager, Client, User, KeyManager

app = FastAPI()
connection_manager = ConnectionManager(DHTNode(8469, [("84.201.160.14", 8468)]))
key_manager = KeyManager('Bob')
client = Client(key_manager.get_user('Bob'), connection_manager)


class Message(BaseModel):
    name: str
    text: str


@app.on_event("startup")
async def app_startup():
    await client.connect()


@app.on_event("shutdown")
def app_shutdown():
    client.connection_manager.node.stop()


@app.get("/healthcheck")
async def healthcheck():
    return 200


# @app.get("/read")
# async def read(message_key: str):
#     result = await connection_manager.get(message_key)
#     return {"message": result}
#
#
# @app.post("/write")
# async def write(message: Message):
#     await connection_manager.set(message.key, message.value)
#     return 200


@app.get("/read_messages")
async def read_messages(name: str):
    user = key_manager.get_user(name)
    return await client.read_messages(user)


@app.post("/send_message")
async def send_message(message: Message):
    user = key_manager.get_user(message.name)
    await client.send_message(user, message.text)
    return 200
