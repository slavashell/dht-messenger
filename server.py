from fastapi import FastAPI, Response
from pydantic import BaseModel

from dht_node.dht_node import DHTNode
from client import ConnectionManager, Client, User
from key_manager import KeyManager

app = FastAPI()
connection_manager = ConnectionManager(DHTNode(8469, [("84.201.160.14", 8468)]))

client = Client(connection_manager)

try:
    key_manager = KeyManager.from_file(".")
    client.set_user(User(name="Bob", public_key=key_manager.public_key, private_key=key_manager.private_key))
except:
    key_manager = KeyManager("", "")


class Message(BaseModel):
    name: str
    text: str


class Chat(BaseModel):
    name: str
    key: str


class Key(BaseModel):
    key: str


@app.on_event("startup")
async def app_startup():
    await client.connect()


@app.on_event("shutdown")
def app_shutdown():
    client.connection_manager.node.stop()


@app.get("/healthcheck")
async def healthcheck():
    return 200


@app.get("/read_messages")
async def read_messages(name: str):
    if not key_manager.initialized:
        return Response(status_code=403)
    try:
        user_key = key_manager.key_by_name(name)
    except KeyError:
        return Response(status_code=404, content=f"User {name} not found")
    return await client.read_messages(User(name=name, public_key=user_key))


@app.post("/send_message")
async def send_message(message: Message):
    if not key_manager.initialized:
        return Response(status_code=403)
    user_key = key_manager.key_by_name(message.name)
    await client.send_message(User(name=message.name, public_key=user_key), message.text)
    return 200


@app.post("/add_chat")
async def add_chat(chat: Chat):
    if not key_manager.initialized:
        return Response(status_code=403)
    key_manager.add_key(chat.name, chat.key)
    return 200


@app.post("/register_user")
async def register_user(key: Key = None):
    key_manager.init(key.key if key is not None else None)
    client.set_user(User(name="Bob", public_key=key_manager.public_key, private_key=key_manager.private_key))
    return 200
