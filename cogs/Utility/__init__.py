from discord.ext import commands

from cogs.Utility.ping import PingCommands
from cogs.Utility.miq import MIQ
from cogs.Utility.roll import Roll
from cogs.Utility.role_giver import RoleGiver


class Utility(commands.Cog, PingCommands, MIQ, Roll, RoleGiver):
    def __init__(self, bot: commands.Bot):
        commands.Cog.__init__(self)
        MIQ.__init__(self, bot)
        PingCommands.__init__(self, bot)
        Roll.__init__(self, bot)
        RoleGiver.__init__(self, bot)


async def setup(bot: commands.Bot):
    await bot.add_cog(Utility(bot))
