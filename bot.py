"""
Roommate Bot — AI-powered hackathon collaboration assistant.
Entry point: Sentry init, file logging, health server, cog loader, graceful shutdown.
"""
from __future__ import annotations

import asyncio
import logging
import logging.handlers
import os
import signal

import discord
from discord.ext import commands
from dotenv import load_dotenv

from config import DISCORD_TOKEN, SENTRY_DSN

load_dotenv()

# ── Logging — console + rotating file ────────────────────────────────────────

def _setup_logging() -> None:
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    console = logging.StreamHandler()
    console.setFormatter(fmt)

    file_handler = logging.handlers.RotatingFileHandler(
        filename="roommate.log",
        maxBytes=5 * 1024 * 1024,  # 5 MB per file
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(console)
    root.addHandler(file_handler)


_setup_logging()
log = logging.getLogger("roommate")

# ── Sentry — optional error monitoring ───────────────────────────────────────

if SENTRY_DSN:
    try:
        import sentry_sdk
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            traces_sample_rate=0.1,
            profiles_sample_rate=0.1,
        )
        log.info("Sentry initialised ✅")
    except ImportError:
        log.warning("sentry-sdk not installed — run: pip install sentry-sdk")

# ── Bot setup ─────────────────────────────────────────────────────────────────

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


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction, error: Exception
) -> None:
    log.error("Slash command error [%s]: %s", interaction.command, error)
    if SENTRY_DSN:
        try:
            import sentry_sdk
            sentry_sdk.capture_exception(error)
        except Exception:
            pass
    msg = "⚠️ Something went wrong. Try again in a moment."
    try:
        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)
    except Exception:
        pass


# ── Main ──────────────────────────────────────────────────────────────────────

async def main() -> None:
    if not DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN is missing — check your .env file")

    # Init Supabase (optional)
    from services import db_service
    db_service.init()

    # Start health server before bot connects so Railway sees it immediately
    from utils.health import start_health_server
    await start_health_server()

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
