from discord.ext import commands

from .message import MessageWatcher
from .member import MemberWatcher


class DiscordEventWatcher(commands.Cog, MessageWatcher, MemberWatcher):
    def __init__(self, bot: commands.Bot):
        commands.Cog.__init__(self)
        MessageWatcher.__init__(self, bot)
        MemberWatcher.__init__(self, bot)


async def setup(bot: commands.Bot):
    await bot.add_cog(DiscordEventWatcher(bot))
