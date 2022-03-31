import asyncio
import typing as tp

from kademlia.network import Server


class DHTServer(Server):
    def __init__(self, ksize=20, alpha=3, node_id=None, storage=None):
        super().__init__(ksize, alpha, node_id, storage)
        self.ping_loop = None

    def ping_neighbors(self):
        asyncio.ensure_future(self._ping_neighbors())
        loop = asyncio.get_event_loop()
        self.ping_loop = loop.call_later(1, self.ping_neighbors)

    async def _ping_neighbors(self):
        neighbors = self.protocol.router.find_neighbors(self.node)
        for node in neighbors:
            await self.protocol.call_ping(node)

    def stop(self):
        if self.transport is not None:
            self.transport.close()

        if self.refresh_loop:
            self.refresh_loop.cancel()

        if self.save_state_loop:
            self.save_state_loop.cancel()

        if self.ping_loop:
            self.ping_loop.cancel()


class DHTNode:
    def __init__(self, port: int, nodes: tp.List[tp.Tuple[str, int]]) -> None:
        self._nodes = nodes
        self._port = port
        self._server = DHTServer()

    async def __aenter__(self) -> "DHTNode":
        await self.connect()
        return self

    def __aexit__(self, exc_type, exc, tb) -> None:
        self.stop()

    async def connect(self) -> None:
        await self._server.listen(self._port)
        await self._server.bootstrap(self._nodes)
        self._server.ping_neighbors()

    def stop(self) -> None:
        self._server.stop()

    async def get(self, key: bytes) -> str:
        return await self._server.get(key)

    async def set(self, key: bytes, val: bytes):
        return await self._server.set(key, val)
