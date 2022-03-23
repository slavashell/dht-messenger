import typing as tp
import json

from nacl.public import PrivateKey

class KeyManager:

    CACHE_FILE = 'cached_keys.json'
    PRIVATE_KEY = 'private.key'
    PUBLIC_KEY = 'public.key'

    def __init__(self, private_key: str, public_key: str, public_keys: tp.Dict[str, str] = None, cache_dir = ".") -> None:
        self._private_key = private_key
        self._public_key = public_key
        self._keys = {} if public_keys is None else public_keys
        self._cache_dir = cache_dir

    @staticmethod
    def key_to_string(key: PrivateKey) -> str:
        return key.__bytes__().hex()

    @staticmethod
    def from_file(path: str) -> 'KeyManager':
        with open(path + '/' + KeyManager.PRIVATE_KEY, 'r') as private_key_file:
            private_key = private_key_file.readlines()
        with open(path + '/' + KeyManager.PUBLIC_KEY, 'r') as public_key_file:
            public_key = public_key_file.readlines()
        with open(path + '/' + KeyManager.CACHE_FILE) as cached_keys:
            keys = json.load(cached_keys)
        return KeyManager(private_key, public_key, keys)

    @staticmethod
    def first_init(path: str) -> 'KeyManager':
        generated_key = PrivateKey.generate()
        private_key = KeyManager.key_to_string(generated_key)
        public_key = KeyManager.key_to_string(generated_key.public_key)
        with open(path + '/private.key', 'w') as private_key_file:
            private_key_file.write(private_key)
        with open(path + '/public.key', 'w') as public_key_file:
            public_key_file.write(public_key)
        return KeyManager(private_key, public_key)

    @property
    def private_key(self) -> str:
        return self._private_key

    @property
    def public_key(self) -> str:
        return self._public_key

    def key_by_name(self, name: str) -> tp.Optional[str]:
        return self._keys.get(name, None)

    def add_key(self, name: str, key: str) -> None:
        self._keys[name] = key
        with open(self._cache_dir + '/' + KeyManager.CACHE_FILE, 'w') as cache_file:
            json.dump(self._keys, cache_file)
