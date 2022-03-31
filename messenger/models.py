import sys
from dataclasses import dataclass

from nacl.public import PrivateKey, PublicKey
from pydantic import BaseModel
import typing as tp


@dataclass
class User:
    public_key: PublicKey
    private_key: PrivateKey = None


class Message(BaseModel):
    text: str
    timestamp: float

    def serialize(self):
        return "{}\n{}".format(self.timestamp, self.text).encode("utf-8")

    @staticmethod
    def deserialize(message: bytes) -> "Message":
        message = message.decode("utf-8")
        try:
            timestamp, text = message.split("\n", 1)
        except ValueError:
            print("Unexpected serialization format: {}".format(message), file=sys.stderr)
            raise ValueError
        return Message(text=text, timestamp=float(timestamp))


class AppMessage(BaseModel):
    name: str
    text: str


class AppChat(BaseModel):
    name: str
    key: str


class AppKey(BaseModel):
    key: str


class UserChats(BaseModel):
    chats: tp.List[str]
