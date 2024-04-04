import asyncio

from aiohttp import web
from aiohttp.test_utils import TestServer
from contextlib import asynccontextmanager
from socketio import AsyncServer, AsyncClient
from tenacity import AsyncRetrying
from tenacity.stop import stop_after_delay
from tenacity.wait import wait_fixed
from typing import AsyncIterator
from unittest.mock import AsyncMock
from yarl import URL


@asynccontextmanager
async def web_server(socketio_server: AsyncServer) -> AsyncIterator[URL]:
    aiohttp_app = web.Application()
    socketio_server.attach(aiohttp_app)

    async def _lifespan(
        server: TestServer, started: asyncio.Event, teardown: asyncio.Event
    ):
        await server.start_server()
        started.set()
        await teardown.wait()
        await server.close()

    setup = asyncio.Event()
    teardown = asyncio.Event()

    server = TestServer(aiohttp_app, port=8328)
    t = asyncio.create_task(_lifespan(server, setup, teardown), name="server-lifespan")

    await setup.wait()

    yield server.make_url("/")

    assert t
    teardown.set()


async def main() -> None:
    socketio_server = AsyncServer(async_mode="aiohttp", engineio_logger=True)

    socketio_client = AsyncClient(logger=True, engineio_logger=True)

    async with web_server(socketio_server) as server_url:
        # observe the disconnect event triggered by the server
        spy_disconnect = AsyncMock(wraps=lambda _: None)
        socketio_server.on("disconnect", spy_disconnect)

        await socketio_client.connect(f"{server_url}", transports=["websocket"])

        # disconnect client and wait for server event delivery
        await socketio_client.disconnect()

        async for attempt in AsyncRetrying(
            wait=wait_fixed(0.1), stop=stop_after_delay(5), reraise=True
        ):
            with attempt:
                assert len(spy_disconnect.call_args_list) == 1
        print("disconnect calls:", spy_disconnect.call_args_list)


if __name__ == "__main__":
    asyncio.run(main())
