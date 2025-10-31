from discord.ext import commands


class DiscordEventWatcher(commands.Cog):
    def __init__(self, bot: commands.Bot):
        commands.Cog.__init__(self)


async def setup(bot: commands.Bot):
    await bot.add_cog(DiscordEventWatcher(bot))
