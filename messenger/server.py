from fastapi import FastAPI, Response

from client import Client
from key_manager import KeyManager
from models import AppChat, AppKey, AppMessage, User
from node import DHTNode

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


@app.get("/public_key", response_model=AppKey)
async def public_key():
    if not key_manager.initialized:
        return Response(status_code=404)
    return AppKey(key=KeyManager.key_to_string(key_manager.public_key))


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
