"""
Community commands: /hello, /verify, /winners, /set-winner, /status
"""
from __future__ import annotations

import logging
import time

import discord
from discord import app_commands
from discord.ext import commands

from config import ROLE_VERIFIED
from services.storage_service import get_winners, save_winner
from utils.helpers import sanitize

log = logging.getLogger("roommate.community")

_start_time = time.time()


class CommunityCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # ── /hello ────────────────────────────────────────────────────────────────

    @app_commands.command(name="hello", description="Say hi to Roommate Bot 👋")
    async def hello(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            f"Hey {interaction.user.mention}! 👋\n"
            "I'm **Roommate Bot** — your AI-powered hackathon teammate finder.\n\n"
            "Try these:\n"
            "• `/hackathons` — browse upcoming events\n"
            "• `/team-match` — find your ideal teammates\n"
            "• `/ask` — get AI help\n"
            "• `/multilingual-help` — help in any language 🌍"
        )

    # ── /verify ───────────────────────────────────────────────────────────────

    @app_commands.command(name="verify", description="Get the Verified Hackeroos role ✅")
    async def verify(self, interaction: discord.Interaction) -> None:
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message(
                "Run this inside a server!", ephemeral=True
            )
            return

        role = discord.utils.get(guild.roles, name=ROLE_VERIFIED)
        if not role:
            await interaction.response.send_message(
                f"⚠️ Role `{ROLE_VERIFIED}` doesn't exist yet. Ask an admin to create it.",
                ephemeral=True,
            )
            return

        member = interaction.user
        if isinstance(member, discord.Member) and role in member.roles:
            await interaction.response.send_message(
                "✅ You're already verified!", ephemeral=True
            )
            return

        try:
            if isinstance(member, discord.Member):
                await member.add_roles(role, reason="Self-verify via /verify")
            await interaction.response.send_message(
                "✅ Verified! Welcome to the crew 🦘⚡", ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "⚠️ I don't have permission to assign that role. "
                "Ask an admin to move my role higher in the server settings.",
                ephemeral=True,
            )

    # ── /winners ──────────────────────────────────────────────────────────────

    @app_commands.command(name="winners", description="Show recent hackathon winners 🏆")
    async def winners(self, interaction: discord.Interaction) -> None:
        data = await get_winners()
        if not data:
            await interaction.response.send_message(
                "🏆 No winners recorded yet.", ephemeral=True
            )
            return

        embed = discord.Embed(title="🏆 Hackathon Winners", color=0xFFBF00)
        for entry in list(data.values())[-3:]:
            embed.add_field(
                name=f"🏁 {entry.get('hackathon', 'Unknown')}",
                value=(
                    f"• **Team:** {entry.get('team', '—')}\n"
                    f"• **Project:** {entry.get('project', '—')}\n"
                    f"• **Prize:** {entry.get('prize', '—')}"
                ),
                inline=False,
            )
        embed.set_footer(text="Use /set-winner to add new winners (admin only)")
        await interaction.response.send_message(embed=embed)

    # ── /set-winner ───────────────────────────────────────────────────────────

    @app_commands.command(
        name="set-winner", description="Record a hackathon winner (admin only) 🏆"
    )
    @app_commands.describe(
        hackathon="Hackathon name",
        team="Winning team name",
        project="Project name",
        prize="Prize won",
    )
    async def set_winner(
        self,
        interaction: discord.Interaction,
        hackathon: str,
        team: str,
        project: str = "—",
        prize: str = "—",
    ) -> None:
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "⚠️ Only admins can record winners.", ephemeral=True
            )
            return

        entry = {
            "hackathon": sanitize(hackathon, 100),
            "team": sanitize(team, 100),
            "project": sanitize(project, 200),
            "prize": sanitize(prize, 100),
        }
        await save_winner(entry["hackathon"], entry)
        await interaction.response.send_message(
            f"✅ Winner saved!\n🏆 **{entry['hackathon']}** → Team **{entry['team']}**",
            ephemeral=True,
        )

    # ── /status ───────────────────────────────────────────────────────────────

    @app_commands.command(name="status", description="Check bot health and stats 📊")
    async def status(self, interaction: discord.Interaction) -> None:
        uptime_s = int(time.time() - _start_time)
        h, remainder = divmod(uptime_s, 3600)
        m, s = divmod(remainder, 60)
        latency_ms = round(self.bot.latency * 1000)
        winners = await get_winners()

        embed = discord.Embed(title="📊 Roommate Bot — Status", color=0x00FF88)
        embed.add_field(name="⚡ Latency", value=f"{latency_ms} ms", inline=True)
        embed.add_field(name="⏱️ Uptime", value=f"{h}h {m}m {s}s", inline=True)
        embed.add_field(name="🌐 Servers", value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="🏆 Winners", value=str(len(winners)), inline=True)
        embed.add_field(name="🤖 Model", value="GPT-4o-mini", inline=True)
        embed.set_footer(text="Roommate Bot • Production")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CommunityCog(bot))
