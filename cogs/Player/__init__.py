from discord.ext import commands
from .main import PlayerMain
from .core.player_setup import PlayerSetup

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Player_Core")


class Player(commands.Cog, PlayerMain, PlayerSetup):
    def __init__(self, bot: commands.Bot):
        commands.Cog.__init__(self)
        PlayerMain.__init__(self, bot)
        PlayerSetup.__init__(self, bot)


async def setup(bot: commands.Bot):
    await bot.add_cog(Player(bot))
