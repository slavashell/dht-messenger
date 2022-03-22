from fastapi import FastAPI
from pydantic import BaseModel

from dht_node.dht_node import DHTNode

app = FastAPI()
node = DHTNode(8469, [("84.201.160.14", 8468)])

class Message(BaseModel):
    key: str
    value: str

@app.on_event('startup')
async def app_startup():
    await node.connect()

@app.on_event("shutdown")
def app_shutdown():
    node.stop()

@app.get("/healthcheck")
async def healthcheck():
    return 200

@app.get("/read")
async def read(message_key: str):
    result = await node.get(message_key)
    return {"message": result}

@app.post("/write")
async def write(message: Message):
    await node.set(message.key, message.value)
    return 200
