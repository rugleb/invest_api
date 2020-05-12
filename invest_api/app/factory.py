import asyncio
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict

import uvloop
from aiohttp import web
from yarl import URL

from invest_api.log import app_logger, setup_logging
from invest_api.settings import get_config

from .middlewares import add_middlewares
from .views import add_routes

__all__ = (
    "create_app",
    "create_tcp_server",
)


def setup_asyncio() -> None:
    uvloop.install()
    loop = asyncio.get_event_loop()

    executor = ThreadPoolExecutor(thread_name_prefix="invest_api")
    loop.set_default_executor(executor)

    def handler(_, context: Dict) -> None:
        message = "Caught asyncio exception: {message}".format_map(context)
        app_logger.warning(message)

    loop.set_exception_handler(handler)


async def create_app(config: Dict = None) -> web.Application:
    setup_logging()
    setup_asyncio()

    app = web.Application(logger=app_logger)
    add_routes(app)
    add_middlewares(app)

    app["config"] = config or get_config()

    return app


@asynccontextmanager
async def create_tcp_server(
        host: str,
        port: int,
        config: Dict = None,
) -> AsyncIterator[URL]:
    app = await create_app(config)
    runner = web.AppRunner(app)

    await runner.setup()

    site = web.TCPSite(runner, host, port, ssl_context=None)
    await site.start()

    try:
        yield URL.build(scheme="http", host=host, port=port)
    finally:
        await runner.cleanup()