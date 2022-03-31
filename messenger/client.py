import base64
import hashlib
from datetime import datetime

from nacl.public import Box
from models import Message, User
from node import DHTNode


class Client:
    def __init__(self, node: DHTNode):
        self.user = None
        self.node = node

    def init(self, user: User):
        self.user = user

    @staticmethod
    def get_genesis_key(user_src: User, user_dst: User) -> bytes:
        return hashlib.sha256(user_src.public_key.__bytes__() + user_dst.public_key.__bytes__()).digest()

    @staticmethod
    def get_next_message_key(message: Message, message_key: bytes) -> bytes:
        return hashlib.sha256(message.serialize() + message_key).digest()

    async def get_message_key(self, user: User) -> bytes:
        message_key = self.get_genesis_key(self.user, user)
        messages = await self.read_messages_from_key(user, message_key)
        if messages:
            message, message_key = messages[-1]
            return self.get_next_message_key(message, message_key)
        return message_key

    async def read_message(self, user: User, message_key: bytes):
        message = await self.node.get(message_key)
        if message is None:
            return None

        message_box = Box(self.user.private_key, user.public_key)
        decrypted_message = message_box.decrypt(base64.b64decode(message))
        return Message.deserialize(decrypted_message)

    async def read_messages_from_key(self, user: User, message_key: bytes):
        messages = []
        while True:
            message = await self.read_message(user, message_key)
            if message is None:
                break
            messages.append((message, message_key))
            message_key = self.get_next_message_key(message, message_key)
        return messages

    async def read_messages(self, user: User):
        me2user_key = self.get_genesis_key(self.user, user)
        user2me_key = self.get_genesis_key(user, self.user)
        me2user = await self.read_messages_from_key(user, me2user_key)
        user2me = await self.read_messages_from_key(user, user2me_key)

        me2user = list(map(lambda message: (message, "You"), me2user))
        user2me = list(map(lambda message: (message, "User"), user2me))
        messages = list(
            map(
                lambda message: "{:<40}\t{} at {}".format(
                    message[0][0].text,
                    message[1],
                    datetime.fromtimestamp(message[0][0].timestamp).strftime("%H:%M %d-%m-%Y"),
                ),
                sorted(me2user + user2me, key=lambda message: message[0][0].timestamp),
            )
        )
        return messages

    async def send_message(self, user: User, text: str):
        message_key = await self.get_message_key(user)
        message = Message(
            text=text,
            timestamp=datetime.timestamp(datetime.utcnow()),
        )
        message_box = Box(self.user.private_key, user.public_key)
        encrypted_message = message_box.encrypt(message.serialize())
        await self.node.set(message_key, base64.b64encode(encrypted_message))
        return message, message_key
