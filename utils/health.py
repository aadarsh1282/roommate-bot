"""
Minimal aiohttp health check server.
Railway requires an HTTP response to confirm the service is alive.
Listens on $PORT (default 8080).
"""
from __future__ import annotations

import logging
import os

from aiohttp import web

log = logging.getLogger("roommate.health")


async def _health(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok", "bot": "roommate-bot"})


async def start_health_server() -> None:
    port = int(os.getenv("PORT", "8080"))
    app = web.Application()
    app.router.add_get("/", _health)
    app.router.add_get("/health", _health)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", port).start()
    log.info("Health server listening on port %d", port)
