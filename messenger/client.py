import base64
import hashlib
from datetime import datetime

from dht.node import DHTNode
from nacl.public import Box
from messenger.models import Message, User


class Client:
    def __init__(self, node: DHTNode):
        self.user = None
        self.node = node

    def init(self, user: User):
        self.user = user

    @staticmethod
    def get_genesis_key(user_src: User, user_dst: User) -> str:
        return hashlib.sha1(user_src.public_key.__bytes__() + user_dst.public_key.__bytes__()).hexdigest()

    async def get_message_key(self, user: User) -> str:
        message_key = self.get_genesis_key(self.user, user)
        messages = await self.read_messages_from_key(user, message_key)
        if messages:
            return messages[-1].next_message_key
        return message_key

    async def read_message(self, user: User, message_key: str):
        message = await self.node.get(message_key)
        if message is None:
            return None

        message_box = Box(self.user.private_key, user.public_key)
        decrypted_message = message_box.decrypt(base64.b64decode(message))
        return Message.parse_raw(decrypted_message)

    async def read_messages_from_key(self, user: User, message_key: str):
        messages = []
        while True:
            message = await self.read_message(user, message_key)
            if message is None:
                break
            message_key = message.next_message_key
            messages.append(message)
        return messages

    async def read_messages(self, user: User):
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

    async def send_message(self, user: User, text: str):
        message_key = await self.get_message_key(user)
        next_message_key = hashlib.sha1(bytes.fromhex(message_key) + text.encode("utf-8")).hexdigest()
        message = Message(
            text=text,
            next_message_key=next_message_key,
            timestamp=datetime.timestamp(datetime.utcnow()),
        )

        message_box = Box(self.user.private_key, user.public_key)
        encrypted_message = message_box.encrypt(message.json().encode("utf-8"))
        await self.node.set(message_key, base64.b64encode(encrypted_message))
        return message, message_key
