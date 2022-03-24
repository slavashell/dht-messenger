import logging
import asyncio

from node import DHTServer

handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
log = logging.getLogger("kademlia")
log.addHandler(handler)
log.setLevel(logging.DEBUG)

server = DHTServer()


def create_bootstrap_node():
    loop = asyncio.get_event_loop()
    loop.set_debug(True)

    loop.run_until_complete(server.listen(8468))
    server.ping_neighbors()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        loop.close()


def main():
    create_bootstrap_node()


if __name__ == "__main__":
    main()
