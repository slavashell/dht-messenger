import logging

from fastapi import FastAPI, Response

from client import Client
from user_manager import UserManager
from models import AppChat, AppKey, AppMessage, User, UserChats
from node import DHTNode

app = FastAPI()
client = Client(DHTNode(8469, [("84.201.160.14", 8468)]))

handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
log = logging.getLogger("kademlia")
log.addHandler(handler)
log.setLevel(logging.DEBUG)

try:
    user_manager = UserManager.from_file(".")
    client.init(User(public_key=user_manager.public_key, private_key=user_manager.private_key))
except Exception as e:
    user_manager = UserManager("", "")


@app.on_event("startup")
async def app_startup():
    await client.node.connect()


@app.on_event("shutdown")
def app_shutdown():
    client.node.stop()


@app.get("/public_key", response_model=AppKey)
async def public_key():
    if not user_manager.initialized:
        return Response(status_code=404)
    return AppKey(key=UserManager.key_to_string(user_manager.public_key))


@app.get("/read_messages")
async def read_messages(name: str):
    if not user_manager.initialized:
        return Response(status_code=403)
    try:
        user_key = user_manager.key_by_name(name)
    except KeyError:
        return Response(status_code=404, content=f"User {name} not found")
    return await client.read_messages(User(public_key=user_key))


@app.post("/send_message")
async def send_message(message: AppMessage):
    if not user_manager.initialized:
        return Response(status_code=403)
    user_key = user_manager.key_by_name(message.name)
    await client.send_message(User(public_key=user_key), message.text)
    return 200


@app.post("/add_chat")
async def add_chat(chat: AppChat):
    if not user_manager.initialized:
        return Response(status_code=403)
    user_manager.add_key(chat.name, chat.key)
    return 200


@app.post("/register_user")
async def register_user(key: AppKey = None):
    user_manager.init(key.key if key is not None else None)
    client.init(User(public_key=user_manager.public_key, private_key=user_manager.private_key))
    return 200


@app.get("/chats", response_model=UserChats)
async def get_chats():
    if not user_manager.initialized:
        return Response(status_code=403)
    return UserChats(chats=user_manager.get_chat_list())
