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
        return self.json().encode("utf-8")


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
