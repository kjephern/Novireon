import discord
from discord.ext import commands

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

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User):
        if before.avatar.key != after.avatar.key:
            event_type = "avatar"
        if before.username != after.username:
            event_type = "username"
        if before.discriminator != after.discriminator:
            event_type = "discriminator"
        server_logger_cog = self.bot.get_cog("ServerLogger")
        await server_logger_cog.member_event(
            before=before, after=after, event_type=event_type
        )
