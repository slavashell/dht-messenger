import json
from nacl.public import PrivateKey

skbob = PrivateKey.generate()
pkbob = skbob.public_key

skalice = PrivateKey.generate()
pkalice = skalice.public_key


def key_to_string(key):
    return key.__bytes__().hex()


keys = {"Bob": key_to_string(pkbob), "Alice": key_to_string(pkalice)}
private_keys = {"Bob": key_to_string(skbob), "Alice": key_to_string(skalice)}

with open("keys.json", "w") as f:
    json.dump(keys, f, indent=4)

with open("private_keys.json", "w") as f:
    json.dump(private_keys, f, indent=4)
