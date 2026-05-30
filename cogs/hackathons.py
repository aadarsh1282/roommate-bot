"""
Hackathon discovery: /hackathons
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands

from services.hackathon_service import fetch_upcoming
from utils.helpers import format_date

log = logging.getLogger("roommate.hackathons")


class HackathonsCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="hackathons",
        description="Browse top upcoming global hackathons 🌍",
    )
    async def hackathons(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        events = await fetch_upcoming()

        if not events:
            embed = discord.Embed(
                title="⚠️ No hackathons found right now",
                description=(
                    "The feed is temporarily unavailable. Browse manually:\n\n"
                    "• [Devpost](https://devpost.com/hackathons)\n"
                    "• [MLH](https://mlh.io/events)\n"
                    "• [Lu.ma](https://lu.ma/tag/hackathon)\n"
                    "• [Hack Club](https://events.hackclub.com)\n"
                    "• [Hackeroos](https://hackeroos.com.au/#whats-on)"
                ),
                color=0xFFA500,
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(
            title="🌍 Upcoming Hackathons",
            description=f"Top **{len(events)}** upcoming events:",
            color=0x00FF88,
            timestamp=datetime.now(timezone.utc),
        )

        for e in events:
            title = (e.get("title") or "Untitled")[:80]
            source = e.get("source", "Unknown")
            location = e.get("location") or "Online"
            start = format_date(e.get("start_date"))
            url = e.get("url") or "#"
            mode = e.get("mode", "")
            mode_tag = f" • {mode}" if mode else ""

            embed.add_field(
                name=title,
                value=f"📅 {start} • 📍 {location}{mode_tag} • [{source}]({url})",
                inline=False,
            )

        embed.set_footer(text="Roommate Bot • Updated daily • /hackathons")
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(HackathonsCog(bot))
