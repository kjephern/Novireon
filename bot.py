import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging
from logging_config import setup_logging


_log = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("DISCORD")
DEFAULT_PREFIX = os.getenv("DEFAULT_PREFIX", "!")

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix=DEFAULT_PREFIX,
    intents=intents,
)


async def load_all_cogs(bot):
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
                    _log.error(
                        f"Failed to load Cog Package {module_path}: {e}", exc_info=True
                    )
    for package in loaded_packages:
        _log.info(f"Loaded Cog Package: {package}")


@bot.event
async def on_ready():
    setup_logging()
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


if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
