from discord.ext import commands

from .setup import ServerLoggerSetup
from .main import ServerLoggerMain


class ServerLogger(commands.Cog, ServerLoggerSetup, ServerLoggerMain):
    def __init__(self, bot: commands.Bot):
        commands.Cog.__init__(self)
        ServerLoggerSetup.__init__(self, bot)
        ServerLoggerMain.__init__(self, bot)


async def setup(bot: commands.Bot):
    await bot.add_cog(ServerLogger(bot))
