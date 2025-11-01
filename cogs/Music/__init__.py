from discord.ext import commands
from .main import MusicMain
from .core.music_setup import MusicSetup

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Music_Core")


class Music(commands.Cog, MusicMain, MusicSetup):
    def __init__(self, bot: commands.Bot):
        commands.Cog.__init__(self)
        MusicMain.__init__(self, bot)
        MusicSetup.__init__(self, bot)


async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
