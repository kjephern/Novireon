from discord.ext import commands

from Novireon.cogs.ServerLogger.main import ServerLoggerMain
from Novireon.cogs.ServerLogger.setup import ServerLoggerSetup


class ServerLogger(commands.Cog, ServerLoggerSetup, ServerLoggerMain):
    def __init__(self, bot: commands.Bot):
        commands.Cog.__init__(self)
        ServerLoggerSetup.__init__(self, bot)
        ServerLoggerMain.__init__(self, bot)


async def setup(bot: commands.Bot):
    await bot.add_cog(ServerLogger(bot))
