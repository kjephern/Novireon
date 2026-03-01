import logging

from discord.ext import commands

from Novireon.cogs.Player.main import PlayerMain
from Novireon.cogs.Player.errors import *
from Novireon.cogs.Player.setup import PlayerSetup


logger = logging.getLogger("Player_Core")
logger.setLevel(logging.INFO)


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
        elif isinstance(error, NotInValidCommandChannel):
            msg = "請使用正確的指令頻道"
        await itat.response.send_message(msg, ephemeral=True)
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(Player(bot))
