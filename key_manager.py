import typing as tp
import json
import os.path

from nacl.public import PrivateKey, PublicKey


class KeyManager:

    CACHE_FILE = "cached_keys.json"
    PRIVATE_KEY = "private.key"
    PUBLIC_KEY = "public.key"

    def __init__(
        self, private_key: str, public_key: str, public_keys: tp.Dict[str, str] = None, cache_dir="."
    ) -> None:
        self._private_key = private_key
        self._public_key = public_key
        self._keys = {} if public_keys is None else public_keys
        self._cache_dir = cache_dir

    @staticmethod
    def key_to_string(key: PrivateKey) -> str:
        return key.__bytes__().hex()

    @staticmethod
    def from_file(path: str) -> "KeyManager":
        with open(path + "/" + KeyManager.PRIVATE_KEY, "r") as private_key_file:
            private_key = private_key_file.readline()
        with open(path + "/" + KeyManager.PUBLIC_KEY, "r") as public_key_file:
            public_key = public_key_file.readline()
        cache_path = path + "/" + KeyManager.CACHE_FILE
        keys = None
        if os.path.isfile(cache_path):
            with open(path + "/" + KeyManager.CACHE_FILE) as cached_keys:
                keys = json.load(cached_keys)
        return KeyManager(private_key, public_key, keys)

    @property
    def private_key(self) -> PublicKey:
        return PrivateKey(bytes.fromhex(self._private_key))

    @property
    def public_key(self) -> PrivateKey:
        return PublicKey(bytes.fromhex(self._public_key))

    @property
    def initialized(self) -> bool:
        return self._private_key != ""

    def save_keys(self, private_key: str, public_key: str) -> None:
        self._private_key = private_key
        self._public_key = public_key
        with open(self._cache_dir + "/" + KeyManager.PRIVATE_KEY, "w") as private_key_file:
            private_key_file.write(private_key)
        with open(self._cache_dir + "/" + KeyManager.PUBLIC_KEY, "w") as public_key_file:
            public_key_file.write(public_key)

    def init(self, key: tp.Optional[str]) -> None:
        new_key = PrivateKey.generate() if key is None else PrivateKey(bytes.fromhex(key))
        private_key = KeyManager.key_to_string(new_key)
        public_key = KeyManager.key_to_string(new_key.public_key)
        self.save_keys(private_key, public_key)

    def key_by_name(self, name: str) -> PublicKey:
        print(self._keys)
        return PublicKey(bytes.fromhex(self._keys[name]))

    def add_key(self, name: str, key: str) -> None:
        self._keys[name] = key
        with open(self._cache_dir + "/" + KeyManager.CACHE_FILE, "w") as cache_file:
            json.dump(self._keys, cache_file)
