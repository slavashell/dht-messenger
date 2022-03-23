from dht.node import DHTNode
from fastapi import FastAPI, Response

from messenger.client import Client
from messenger.key_manager import KeyManager
from messenger.models import AppChat, AppKey, AppMessage, User

app = FastAPI()
client = Client(DHTNode(8469, [("84.201.160.14", 8468)]))

try:
    key_manager = KeyManager.from_file(".")
    client.init(User(public_key=key_manager.public_key, private_key=key_manager.private_key))
except:
    key_manager = KeyManager("", "")


@app.on_event("startup")
async def app_startup():
    await client.node.connect()


@app.on_event("shutdown")
def app_shutdown():
    client.node.stop()


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
    return await client.read_messages(User(public_key=user_key))


@app.post("/send_message")
async def send_message(message: AppMessage):
    if not key_manager.initialized:
        return Response(status_code=403)
    user_key = key_manager.key_by_name(message.name)
    await client.send_message(User(public_key=user_key), message.text)
    return 200


@app.post("/add_chat")
async def add_chat(chat: AppChat):
    if not key_manager.initialized:
        return Response(status_code=403)
    key_manager.add_key(chat.name, chat.key)
    return 200


@app.post("/register_user")
async def register_user(key: AppKey = None):
    key_manager.init(key.key if key is not None else None)
    client.init(User(public_key=key_manager.public_key, private_key=key_manager.private_key))
    return 200
