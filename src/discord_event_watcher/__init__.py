from discord.ext import commands

from src.discord_event_watcher.message import MessageWatcher
from src.discord_event_watcher.member import MemberWatcher


class DiscordEventWatcher(commands.Cog, MessageWatcher, MemberWatcher):
    def __init__(self, bot: commands.Bot):
        commands.Cog.__init__(self)
        MessageWatcher.__init__(self, bot)
        MemberWatcher.__init__(self, bot)


async def setup(bot: commands.Bot):
    await bot.add_cog(DiscordEventWatcher(bot))
