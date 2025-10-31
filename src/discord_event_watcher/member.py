import time

import discord
from discord.ext import commands

from cogs.ServerLogger.main import ServerLoggerMain as SLM

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("discord_event_watcher.member")


class MemberWatcher:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.nick != after.nick:
            event_type = "nick"
        if before.roles != after.roles:
            event_type = "role"
        if before.guild_avatar != after.guild_avatar:
            event_type = "guild_avatar"
        if before.pending != after.pending:
            event_type = "pending"
        server_logger_cog = self.bot.get_cog("ServerLogger")
        await server_logger_cog.member_event(
            before=before, after=after, event_type=event_type
        )
