from dataclasses import dataclass

from nacl.public import PrivateKey, PublicKey
from pydantic import BaseModel


@dataclass
class User:
    public_key: PublicKey
    private_key: PrivateKey = None


class Message(BaseModel):
    text: str
    next_message_key: str
    timestamp: float


class AppMessage(BaseModel):
    name: str
    text: str


class AppChat(BaseModel):
    name: str
    key: str


class AppKey(BaseModel):
    key: str
