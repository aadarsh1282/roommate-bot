"""
AI commands: /ask (with memory), /roast-me, /multilingual-help
Rate limited per user. /ask maintains conversation context across calls.
"""
from __future__ import annotations

import logging

import discord
from discord import app_commands
from discord.ext import commands

from config import ROAST_SYSTEM, ASK_COOLDOWN, ROAST_COOLDOWN, MULTILINGUAL_COOLDOWN
from services.memory_service import add_exchange, get_history
from services.openai_service import chat, chat_with_history
from services.translation_service import multilingual_answer
from utils.rate_limiter import cooldown

log = logging.getLogger("roommate.ai")


class AICog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # ── /ask ─────────────────────────────────────────────────────────────────

    @app_commands.command(name="ask", description="Ask the AI assistant anything 🤖")
    @app_commands.describe(question="Your question")
    @cooldown(ASK_COOLDOWN)
    async def ask(self, interaction: discord.Interaction, question: str) -> None:
        await interaction.response.defer()
        try:
            # Build messages: history + new question
            history = get_history(interaction.user.id)
            messages = [*history, {"role": "user", "content": question}]
            answer = await chat_with_history(messages, max_tokens=400)

            # Save exchange to memory
            add_exchange(interaction.user.id, question, answer)

            embed = discord.Embed(
                title="🤖 Roommate AI",
                description=answer,
                color=0x5865F2,
            )
            embed.set_footer(
                text=f"Asked by {interaction.user.display_name} • "
                     f"Context: {len(history) // 2 + 1} message(s)"
            )
            await interaction.followup.send(embed=embed)

        except Exception as e:
            log.error("/ask failed: %s", e)
            await interaction.followup.send(
                "⚠️ AI is temporarily unavailable. Try again in a moment!",
                ephemeral=True,
            )

    # ── /roast-me ─────────────────────────────────────────────────────────────

    @app_commands.command(name="roast-me", description="Get a harmless Gen Z developer roast 😂")
    @cooldown(ROAST_COOLDOWN)
    async def roast_me(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        try:
            roast = await chat(
                f"Roast a hackathon developer named '{interaction.user.display_name}'. "
                "One short roast only. Keep it about coding or hackathon habits.",
                system=ROAST_SYSTEM,
                max_tokens=80,
                temperature=0.95,
            )
            embed = discord.Embed(description=f"🔥 {roast}", color=0xFF6B35)
            embed.set_author(
                name=f"{interaction.user.display_name} just got roasted",
                icon_url=interaction.user.display_avatar.url,
            )
            embed.set_footer(text="All in good fun 😄 • /roast-me")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            log.error("/roast-me failed: %s", e)
            await interaction.followup.send(
                "⚠️ Roast generator is on a coffee break. Try again!",
                ephemeral=True,
            )

    # ── /multilingual-help ────────────────────────────────────────────────────

    @app_commands.command(
        name="multilingual-help",
        description="Ask in any language — get help in your language 🌍",
    )
    @app_commands.describe(question="Your question in any language")
    @cooldown(MULTILINGUAL_COOLDOWN)
    async def multilingual_help(
        self, interaction: discord.Interaction, question: str
    ) -> None:
        await interaction.response.defer()
        try:
            answer = await multilingual_answer(question)
            embed = discord.Embed(
                title="🌍 Multilingual Assistant",
                description=answer,
                color=0x00B4D8,
            )
            embed.set_footer(
                text="Roommate Bot • 🇳🇵 🇮🇳 🇹🇷 🇨🇳 🇦🇺 and more"
            )
            await interaction.followup.send(embed=embed)

        except Exception as e:
            log.error("/multilingual-help failed: %s", e)
            await interaction.followup.send(
                "⚠️ Translation service unavailable. Try again!",
                ephemeral=True,
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AICog(bot))
