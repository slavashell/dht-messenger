from fastapi import FastAPI
from pydantic import BaseModel

from dht_node.dht_node import DHTNode
from client import ConnectionManager, Client, User
from key_manager import KeyManager

app = FastAPI()
connection_manager = ConnectionManager(DHTNode(8469, [("84.201.160.14", 8468)]))

# FIXME(slavashel): move this init to server handlers
try:
    key_manager = KeyManager.from_file(".")
except:
    key_manager = KeyManager.first_init(".")
client = Client(User(name="Bob", public_key=key_manager.public_key, private_key=key_manager.private_key), connection_manager)


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


@app.get("/read_messages")
async def read_messages(name: str):
    user = key_manager.get_user(name)
    return await client.read_messages(user)


@app.post("/send_message")
async def send_message(message: Message):
    user = key_manager.get_user(message.name)
    await client.send_message(user, message.text)
    return 200
