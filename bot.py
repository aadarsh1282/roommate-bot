"""
Roommate Bot — AI-powered hackathon collaboration assistant.

Entry point: loads all cogs, handles graceful shutdown.
"""
from __future__ import annotations

import asyncio
import logging
import signal

import discord
from discord.ext import commands
from dotenv import load_dotenv

from config import DISCORD_TOKEN

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("roommate")

COGS = [
    "cogs.ai",
    "cogs.hackathons",
    "cogs.teams",
    "cogs.community",
    "cogs.moderation",
]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

_stop_event = asyncio.Event()


def _request_stop() -> None:
    _stop_event.set()


@bot.event
async def on_ready() -> None:
    log.info("Roommate Bot online | Guilds: %d", len(bot.guilds))
    await bot.change_presence(
        activity=discord.Game(name="Matching hackathon teams ⚡"),
        status=discord.Status.online,
    )
    try:
        synced = await bot.tree.sync()
        log.info("Synced %d slash commands globally", len(synced))
    except Exception as e:
        log.warning("Slash command sync failed: %s", e)


async def main() -> None:
    if not DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN is missing — check your .env file")

    async with bot:
        for cog in COGS:
            try:
                await bot.load_extension(cog)
                log.info("Loaded: %s", cog)
            except Exception as e:
                log.error("Failed to load %s: %s", cog, e)

        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, _request_stop)
            except NotImplementedError:
                pass  # Windows

        runner = asyncio.create_task(bot.start(DISCORD_TOKEN))
        stopper = asyncio.create_task(_stop_event.wait())

        done, pending = await asyncio.wait(
            {runner, stopper}, return_when=asyncio.FIRST_COMPLETED
        )

        if stopper in done:
            log.info("Shutdown signal received — closing bot...")
            await bot.close()

        for task in pending:
            task.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Stopped via keyboard interrupt")
