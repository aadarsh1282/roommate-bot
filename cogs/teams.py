"""Team matching: /team-match with rate limiting."""
from __future__ import annotations

import logging

import discord
from discord import app_commands
from discord.ext import commands

from config import TEAM_MATCH_COOLDOWN
from services.team_service import find_matches, register_profile
from utils.rate_limiter import cooldown

log = logging.getLogger("roommate.teams")


class TeamProfileModal(discord.ui.Modal, title="Register Your Hacker Profile"):
    skills = discord.ui.TextInput(
        label="Your Skills",
        placeholder="e.g. Python, React, ML, UI/UX, Figma...",
        max_length=200,
    )
    interests = discord.ui.TextInput(
        label="Interests & Hackathon Goals",
        placeholder="What do you want to build? e.g. fintech app, AI tool...",
        max_length=200,
    )
    timezone = discord.ui.TextInput(
        label="Your Timezone",
        placeholder="e.g. AEST, UTC+5:30, EST, GMT+8",
        max_length=50,
    )
    experience = discord.ui.TextInput(
        label="Experience Level",
        placeholder="Beginner / Intermediate / Advanced",
        max_length=50,
    )
    looking_for = discord.ui.TextInput(
        label="Looking For in Teammates",
        placeholder="e.g. frontend dev, ML engineer, designer, PM...",
        max_length=200,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)

        profile = {
            "skills": self.skills.value,
            "interests": self.interests.value,
            "timezone": self.timezone.value,
            "experience": self.experience.value,
            "looking_for": self.looking_for.value,
        }

        await register_profile(
            str(interaction.user.id),
            interaction.user.display_name,
            profile,
        )

        try:
            matches = await find_matches(str(interaction.user.id), profile)
            embed = discord.Embed(
                title="🧑‍🤝‍🧑 Your Team Matches",
                description=matches,
                color=0xFFBF00,
            )
            embed.set_footer(
                text="Profile saved ✅ • Run /team-match again to refresh • Roommate Bot"
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            log.error("Team matching error: %s", e)
            await interaction.followup.send(
                "✅ Profile saved! AI matching temporarily unavailable — "
                "run `/team-match` again in a moment.",
                ephemeral=True,
            )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        log.error("Modal error: %s", error)
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "⚠️ Something went wrong. Please try again.", ephemeral=True
            )


class TeamsCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="team-match",
        description="Find your perfect hackathon teammates with AI 🧑‍🤝‍🧑",
    )
    @cooldown(TEAM_MATCH_COOLDOWN)
    async def team_match(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_modal(TeamProfileModal())


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TeamsCog(bot))
