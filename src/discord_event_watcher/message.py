import discord
from discord.ext import commands

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("discord_event_watcher.message")


class MessageWatcher:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.add_listener

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if after.author.bot:
            return

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return
