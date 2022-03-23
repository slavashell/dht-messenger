import typing as tp

from kademlia.network import Server


class DHTNode:
    def __init__(self, port: int, nodes: tp.List[tp.Tuple[str, int]]) -> None:
        self._nodes = nodes
        self._port = port
        self._server = Server(ksize=1)

    async def __aenter__(self) -> "DHTNode":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.client.quit()

    async def connect(self) -> None:
        await self._server.listen(self._port)
        await self._server.bootstrap(self._nodes)

    def stop(self) -> None:
        self._server.stop()

    async def get(self, key: str) -> str:
        return await self._server.get(key)

    async def set(self, key: str, val: str):
        return await self._server.set(key, val)
