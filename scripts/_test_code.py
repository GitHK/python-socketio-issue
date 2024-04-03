import asyncio
import pytest
from socketio import AsyncServer, AsyncClient


@pytest.fixture
async def web_server(
    socketio_server: AsyncServer, unused_tcp_port_factory: Callable[[], int]
) -> AsyncIterator[URL]:
    """
    this emulates the webserver setup: socketio server with
    an aiopika manager that attaches an aiohttp web app
    """
    aiohttp_app = web.Application()
    socketio_server.attach(aiohttp_app)

    async def _lifespan(
        server: TestServer, started: asyncio.Event, teardown: asyncio.Event
    ):
        # NOTE: this is necessary to avoid blocking comms between client and this server
        await server.start_server()
        started.set()  # notifies started
        await teardown.wait()  # keeps test0server until needs to close
        await server.close()

    setup = asyncio.Event()
    teardown = asyncio.Event()

    server = TestServer(aiohttp_app, port=unused_tcp_port_factory())
    t = asyncio.create_task(_lifespan(server, setup, teardown), name="server-lifespan")

    await setup.wait()

    yield URL(server.make_url("/"))

    assert t
    teardown.set()


@pytest.fixture
async def server_url(web_server: URL) -> str:
    return f'{web_server.with_path("/")}'



async def get_server() -> AsyncServer:
    return AsyncServer(async_mode="aiohttp", engineio_logger=True)


async def get_client() -> AsyncClient:
    return AsyncClient(logger=True, engineio_logger=True)


async def main() -> None:
    server_url = "http://localhost:8080"
    server = await get_server()

    client = await get_client()
    await client.connect(f"{server_url}", transports=["websocket"])


if __name__ == "__main__":
    asyncio.run(main())
    print("done")
