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

    @classmethod
    def deserialize(cls, message: bytes) -> "Message":
        timestamp, text = message.decode("utf-8").split("\n", 1)
        return cls(text=text, timestamp=float(timestamp))


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
