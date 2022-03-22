import asyncio
import base64
import hashlib
import json
from datetime import datetime

from nacl.public import Box, PrivateKey, PublicKey
from pydantic import BaseModel

from dht_node.dht_node import DHTNode


class KeyManager:
    def __init__(self, useraname):
        self.keys = json.load(open("keys.json"))
        self.private_key = json.load(open("private_keys.json"))[useraname]

    def get_public_key(self, username):
        return PublicKey(bytes.fromhex(self.keys[username]))

    def get_private_key(self):
        return PrivateKey(bytes.fromhex(self.private_key))

    def get_initial_chat_key(self, user_src, user_dst):
        return hashlib.sha1(
            bytes.fromhex(self.keys[user_src]) + bytes.fromhex(self.keys[user_dst])
        ).hexdigest()


class ConnectionManager:
    def __init__(self):
        self.node = DHTNode(8469, [("84.201.160.14", 8468)])


class HistoryManager:
    def __init__(self):
        self.send_keys = {}
        self.receive_keys = {}

    def get_send_key(self, username):
        return self.send_keys.get(username)

    def update_on_send(self, username, next_message_key):
        self.send_keys[username] = next_message_key

    def update_on_receive(self, username, next_message_key):
        self.receive_keys[username] = next_message_key


class User(BaseModel):
    name: str


class Message(BaseModel):
    text: str
    next_message_key: str
    timestamp: int


class Client:
    def __init__(self, user, connection_manager):
        self.user = user
        self.key_namager = KeyManager(user.name)
        self.history_mannager = HistoryManager()
        self.connection_manager = connection_manager

    async def connect(self):
        await self.connection_manager.node.connect()

    def get_send_key(self, username):
        send_key = self.history_mannager.get_send_key(username)
        if not send_key:
            self.history_mannager.update_on_send(
                username,
                self.key_namager.get_initial_chat_key(self.user.name, username),
            )
        return self.history_mannager.get_send_key(username)

    async def send_message(self, username, text):
        message_key = self.get_send_key(username)
        message_box = Box(
            self.key_namager.get_private_key(),
            self.key_namager.get_public_key(username),
        )
        next_message_key = hashlib.sha1(text.encode("utf-8")).hexdigest()
        message = Message(
            text=text,
            next_message_key=next_message_key,
            timestamp=int(datetime.timestamp(datetime.utcnow())),
        )
        encrypted_message = message_box.encrypt(message.json().encode("utf-8"))
        await self.connection_manager.node.set(
            message_key, base64.b64encode(encrypted_message)
        )
        self.history_mannager.update_on_send(username, next_message_key)
        return message, message_key

    async def receive_message(self, username, message_key):
        message = await self.connection_manager.node.get(message_key)
        if message is None:
            return None
        message_box = Box(
            self.key_namager.get_private_key(),
            self.key_namager.get_public_key(username),
        )
        decrypted_message = message_box.decrypt(base64.b64decode(message))
        return Message.parse_raw(decrypted_message)

    async def receive_message_chain(self, username):
        message_key = self.key_namager.get_initial_chat_key(username, self.user.name)
        message_chain = []
        while True:
            message = await self.receive_message(username, message_key)
            if message is None:
                break
            message_key = message.next_message_key
            message_chain.append(message)
        return message_chain


async def main():
    connection_manager = ConnectionManager()
    await connection_manager.node.connect()

    bob_client = Client(User(name="Bob"), connection_manager)
    alice_client = Client(User(name="Alice"), connection_manager)

    for i in range(10):
        message, message_key = await bob_client.send_message(
            "Alice", "this is message number {}".format(i)
        )
        print(message, message_key)

    message_chain = await alice_client.receive_message_chain("Bob")
    print(*message_chain, sep="\n")


if __name__ == "__main__":
    asyncio.run(main())
