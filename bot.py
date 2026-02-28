import discord
import logging
import os

from discord.ext import commands
from dotenv import load_dotenv
from logging_config import setup_logging

from cogs.Utility.role_giver import RoleGiverView

_log = logging.getLogger(__name__)


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def setup_hook(self):
        self.add_view(RoleGiverView())


bot = Bot()


@bot.event
async def on_ready():
    await load_all_cogs(bot)
    _log.info(f"Logged in as {bot.user.name} ({bot.user.id})")
    _log.info("syncing...")
    await bot.tree.sync()
    for guild in bot.guilds:
        print(f"- 伺服器: {guild.name} (ID: {guild.id})")
    _log.info(">>Bot is online<<")


@bot.event
async def on_disconnect():
    _log.info("Bot disconnected.")


async def load_all_cogs(bot: commands.Bot):
    loaded_packages = []
    base_dirs = ["cogs", "src"]
    for base in base_dirs:
        for item_name in os.listdir(base):
            item_path = os.path.join(base, item_name)
            if os.path.isdir(item_path) and "__init__.py" in os.listdir(item_path):
                module_path = f"{base}.{item_name}"
                try:
                    await bot.load_extension(module_path)
                    loaded_packages.append(module_path)
                except Exception as e:
                    _log.error(f"Failed to load Cog Package {module_path}: {e}", exc_info=True)
    for package in loaded_packages:
        _log.info(f"Loaded Cog Package: {package}")


if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("DISCORD")
    if TOKEN:
        setup_logging()
        bot.run(TOKEN)
