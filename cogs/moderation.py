"""
Light moderation — emoji spam + mention spam only.
No word filters, no blocked lists, no regex censorship.
"""
from __future__ import annotations

import logging
import re

import discord
from discord.ext import commands

from config import EMOJI_SPAM_THRESHOLD, MENTION_SPAM_THRESHOLD

log = logging.getLogger("roommate.moderation")

_EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001F5FF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "☀-⛿"
    "✀-➿"
    "]+",
    flags=re.UNICODE,
)


class ModerationCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        if not isinstance(message.channel, discord.TextChannel):
            return
        if message.author.guild_permissions.administrator:
            return

        content = message.content or ""

        # Emoji spam
        emoji_count = len(_EMOJI_RE.findall(content))
        if emoji_count >= EMOJI_SPAM_THRESHOLD:
            try:
                await message.delete()
                await message.channel.send(
                    f"{message.author.mention} Easy on the emojis! 😅",
                    delete_after=6,
                )
            except discord.Forbidden:
                pass
            return

        # Mention spam
        mention_count = (
            len(message.mentions)
            + (5 if message.mention_everyone else 0)
            + len(message.role_mentions) * 2
        )
        if mention_count >= MENTION_SPAM_THRESHOLD:
            try:
                await message.delete()
                await message.channel.send(
                    f"{message.author.mention} Too many mentions at once — cool it!",
                    delete_after=6,
                )
            except discord.Forbidden:
                pass
            return


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ModerationCog(bot))
