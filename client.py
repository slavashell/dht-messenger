import asyncio
import base64
import hashlib
from dataclasses import dataclass
from datetime import datetime

from nacl.public import Box, PrivateKey, PublicKey
from pydantic import BaseModel

from dht_node.dht_node import DHTNode

@dataclass
class User:
    name: str
    public_key: PublicKey
    private_key: PrivateKey = None

class Message(BaseModel):
    text: str
    next_message_key: str
    timestamp: float

class ConnectionManager:
    def __init__(self, node: DHTNode):
        self.node = node


class HistoryManager:
    def __init__(self):
        self.user2next_message_key = {}

    def get_next_message_key(self, user):
        return self.user2next_message_key.get(user.name)

    def update_next_message_key(self, user, next_message_key):
        self.user2next_message_key[user.name] = next_message_key


class Client:
    def __init__(self, user, connection_manager):
        self.user = user
        self.history_manager = HistoryManager()
        self.connection_manager = connection_manager

    async def connect(self):
        await self.connection_manager.node.connect()

    @staticmethod
    def get_genesis_key(user_src: User, user_dst: User) -> str:
        return hashlib.sha1(user_src.public_key.__bytes__() + user_dst.public_key.__bytes__()).hexdigest()

    async def get_message_key(self, user: User) -> str:
        message_key = self.history_manager.get_next_message_key(user)
        if not message_key:
            message_key = self.get_genesis_key(self.user, user)
            messages = await self.read_messages_from_key(user, message_key)
            if messages:
                return messages[-1].next_message_key
        return message_key

    async def read_message(self, user, message_key):
        message = await self.connection_manager.node.get(message_key)
        if message is None:
            return None

        message_box = Box(self.user.private_key, user.public_key)
        decrypted_message = message_box.decrypt(base64.b64decode(message))
        return Message.parse_raw(decrypted_message)

    async def read_messages_from_key(self, user, message_key):
        messages = []
        while True:
            message = await self.read_message(user, message_key)
            if message is None:
                break
            message_key = message.next_message_key
            messages.append(message)
        return messages

    async def read_messages(self, user):
        me2user_key = self.get_genesis_key(self.user, user)
        user2me_key = self.get_genesis_key(user, self.user)
        me2user = await self.read_messages_from_key(user, me2user_key)
        user2me = await self.read_messages_from_key(user, user2me_key)
        messages = list(
            map(
                lambda message: (message.text, message.timestamp),
                sorted(me2user + user2me, key=lambda message: message.timestamp),
            )
        )
        return messages

    async def send_message(self, user, text):
        message_key = await self.get_message_key(user)
        message_box = Box(self.user.private_key, user.public_key)
        next_message_key = hashlib.sha1(bytes.fromhex(message_key) + text.encode("utf-8")).hexdigest()

        message = Message(
            text=text,
            next_message_key=next_message_key,
            timestamp=datetime.timestamp(datetime.utcnow()),
        )

        encrypted_message = message_box.encrypt(message.json().encode("utf-8"))
        await self.connection_manager.node.set(message_key, base64.b64encode(encrypted_message))
        self.history_manager.update_next_message_key(user, next_message_key)
        return message, message_key


async def main():
    connection_manager = ConnectionManager()
    await connection_manager.node.connect()

    bob = User(name="Bob", public_key="243189f06df4a71acf01f42c6321db7bc3d167ce94437417981275e44a5fdb32", private_key="8d2223beabd887ddbe4b605cd05276ee9ebd7235ef6f62a68659da0952ba176e")
    alice = User(name="Alice", public_key="0795d9c2ca06ba34ac9a9a9a2a3623e6af935ee48db32551cf599d34b9b0cf45", private_key="d934ad03d4c82ef62216e98bd62066342208fcad9d47872875253b43abf07857")

    bob_client = Client(bob, connection_manager)
    alice_client = Client(alice, connection_manager)

    for i in range(5):
        await bob_client.send_message(alice, "From Bob number {}".format(i))
        await alice_client.send_message(bob, "From Alice number {}".format(i))

    messages = await alice_client.read_messages(bob)
    print(*messages, sep="\n")


if __name__ == "__main__":
    asyncio.run(main())
