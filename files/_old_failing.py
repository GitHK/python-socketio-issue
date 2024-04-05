import asyncio
import logging
import threading
import httpx

from aiohttp import web
from contextlib import asynccontextmanager
from socketio import AsyncServer, AsyncClient
from typing import AsyncIterator, Final
from unittest.mock import AsyncMock


SERVER_PORT: Final[int] = 8328

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(pathname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_logger = logging.getLogger(__name__)


async def start_server(
    stop_event: threading.Event, socketio_server: AsyncServer
) -> None:
    async def handle_default(request):
        return web.Response(text="This is the default route!")

    aiohttp_app = web.Application()
    aiohttp_app.router.add_get("/", handle_default)
    socketio_server.attach(aiohttp_app)

    runner = web.AppRunner(aiohttp_app)
    await runner.setup()

    tcp_server = await asyncio.get_event_loop().create_server(
        runner.server, "0.0.0.0", SERVER_PORT
    )
    _logger.info("Server started")

    stop_event.wait()

    # Cleanup when the event is set
    tcp_server.close()
    await tcp_server.wait_closed()
    await runner.cleanup()
    _logger.info("Server stopped")


def _async_thread_worker(stop_event: threading.Event, socketio_server: AsyncServer):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_server(stop_event, socketio_server))


@asynccontextmanager
async def server_runner() -> AsyncIterator[None]:
    socketio_server = AsyncServer(
        async_mode="aiohttp", logger=True, engineio_logger=True
    )
    # observe the disconnect event triggered by the server
    spy_disconnect = AsyncMock(wraps=lambda _: None)
    socketio_server.on("disconnect", spy_disconnect)

    stop_event = threading.Event()
    server_thread = threading.Thread(
        target=_async_thread_worker, args=(stop_event, socketio_server)
    )
    server_thread.start()

    try:
        await asyncio.sleep(0.5)
        yield
    finally:
        stop_event.set()
        server_thread.join()

    await asyncio.sleep(1)
    assert len(spy_disconnect.call_args_list) == 1


async def main() -> None:
    async with server_runner():
        server_url = f"http://localhost:{SERVER_PORT}/"

        result = await httpx.get(server_url, timeout=1)
        assert result.text == ""

        socketio_client = AsyncClient(logger=True, engineio_logger=True)
        await socketio_client.connect(server_url, transports=["websocket"])

        # disconnect client and wait for server event delivery
        await socketio_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
