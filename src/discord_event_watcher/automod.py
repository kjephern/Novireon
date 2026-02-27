import discord
import logging

from discord.ext import commands

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("discord_event_watcher.automod")


class AutomodWatcher:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_automod_rule_create(self, rule: discord.AutoModRule):
        pass

    @commands.Cog.listener()
    async def on_automod_rule_update(self, rule: discord.AutoModRule):
        pass

    @commands.Cog.listener()
    async def on_automod_rule_delete(self, rule: discord.AutoModRule):
        pass

    @commands.Cog.listener()
    async def on_automod_action(self, execution: discord.AutoModAction):
        pass
