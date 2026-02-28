import discord
import logging

from discord.ext import commands

logger = logging.getLogger("discord_event_watcher.message").setLevel(logging.INFO)


class MessageWatcher:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
        before = payload.cached_message or None
        after = payload.message or None
        if after is None or after.author.bot:
            return
        if before is None or before.content == after.content:
            return
        server_logger_cog = self.bot.get_cog("ServerLogger")
        await server_logger_cog.message_event(before=before, after=after, event_type="edit")

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        before = payload.cached_message or None
        if not before or before.author.bot:
            return
        server_logger_cog = self.bot.get_cog("ServerLogger")
        await server_logger_cog.message_event(before=before, after=None, event_type="delete")
