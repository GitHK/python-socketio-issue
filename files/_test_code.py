import asyncio
import logging

from aiohttp import web
from contextlib import asynccontextmanager
from socketio import AsyncServer, AsyncClient
from unittest.mock import AsyncMock

SERVER_PORT = 8313
SERVER_URL = f"http://localhost:{SERVER_PORT}"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(pathname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_logger = logging.getLogger(__name__)


@asynccontextmanager
async def run_server() -> None:
    socketio_server = AsyncServer(
        async_mode="aiohttp", logger=True, engineio_logger=True
    )
    # observe the disconnect event triggered by the server
    spy_disconnect = AsyncMock(wraps=lambda _: None)
    socketio_server.on("disconnect", spy_disconnect)

    app = web.Application()
    socketio_server.attach(app)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "localhost", SERVER_PORT)
    await site.start()

    _logger.error("Server started")

    yield

    await site.stop()
    await runner.cleanup()

    _logger.error("Server stopped")
    assert len(spy_disconnect.call_args_list) == 1
    _logger.error("TEST OK")


async def main():
    async with run_server():
        # do disconnect
        socketio_client = AsyncClient(logger=True, engineio_logger=True)
        await socketio_client.connect(SERVER_URL, transports=["websocket"])

        # disconnect client and wait for server event delivery
        await socketio_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
