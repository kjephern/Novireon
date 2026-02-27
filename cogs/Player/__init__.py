import logging

from discord.ext import commands

from cogs.Player.main import PlayerMain
from cogs.Player.core.errors import *
from cogs.Player.core.setup import PlayerSetup


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Player_Core")


class Player(commands.Cog, PlayerMain, PlayerSetup):
    def __init__(self, bot: commands.Bot):

        commands.Cog.__init__(self)
        PlayerMain.__init__(self, bot)
        PlayerSetup.__init__(self, bot)

    async def cog_app_command_error(self, itat, error):
        if isinstance(error, NotInValidVoiceChannel):
            msg = "請加入有效的語音頻道"
        elif isinstance(error, NotDJ):
            msg = "你沒有 DJ 權限"
        await itat.response.send_message(msg, ephemeral=True)
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(Player(bot))
