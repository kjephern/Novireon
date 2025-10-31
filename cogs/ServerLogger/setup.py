import os

import discord
from discord import app_commands
from discord.ext import commands

from .utils import Utils

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("server_logger.setup")

from pymongo import MongoClient
from mongo_crud import MongoCRUD

mongo_uri = os.getenv("MONGO_URI")
mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=15000)
db_handler = MongoCRUD(
    client=mongo_client,
    db_name="Norvireon_bot_db",
    collection_name="Server_logger_data",
    logger=logger,
)


class ServerLoggerSetup:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    server_logger = app_commands.Group(
        name="server_logger",
        description="Server logging setting commands.",
        allowed_installs=app_commands.AppInstallationType(guild=True, user=False),
        default_permissions=discord.Permissions(administrator=True),
    )

    @server_logger.command(name="toggle", description="啟用或停用伺服器日誌記錄。")
    @app_commands.guild_install()
    async def toggle_logging(self, itat: discord.Interaction):
        guild_id = itat.guild_id
        data = db_handler.get(query={"_id": guild_id})

        async def enable():
            db_handler.update_one(
                query={"_id": guild_id},
                new_values={"settings.is_logging_enabled": True},
                upsert=True,
            )
            logger.info(
                f"Enabled server logging for guild: {itat.guild.name}-{guild_id}"
            )
            await itat.response.send_message("伺服器日誌已啟用。", ephemeral=True)

        async def disable():
            db_handler.update_one(
                query={"_id": guild_id},
                new_values={"settings.is_logging_enabled": False},
                upsert=True,
            )
            logger.info(
                f"Disabled server logging for guild: {itat.guild.name}-{guild_id}"
            )
            await itat.response.send_message("伺服器日誌已停用。", ephemeral=True)

        if data:
            data = data[0]
        else:
            await enable()
            return

        if_enabled = data.get("settings", {}).get("is_logging_enabled", False)
        # 切換至停用
        if if_enabled:
            await disable()
            return
        # 切換至啟用
        else:
            await enable()
            return

    @server_logger.command(name="list_settings", description="列出伺服器日誌設定。")
    @app_commands.guild_install()
    async def list_settings(self, itat: discord.Interaction):
        await itat.response.defer(ephemeral=True)
        guild_id = itat.guild_id
        data = db_handler.get(query={"_id": guild_id})
        if data:
            data = data[0]
        else:
            await itat.response.send_message(
                "尚未設定伺服器日誌。請使用 /server_logger toggle 來啟用日誌記錄。",
                ephemeral=True,
            )
            return
        settings = data.get("settings", {})
        is_logging_enabled = settings.get("is_logging_enabled", False)
        logging_channel_id = settings.get("logging_channel_id", {})
        embed = discord.Embed(title="伺服器日誌設定")
        embed.add_field(
            name="是否啟用日誌", value=str(is_logging_enabled), inline=False
        )
        for key in logging_channel_id:
            if key == "ignore":
                continue
            channel = self.bot.get_channel(logging_channel_id[key])
            if not channel:
                channel = self.bot.fetch_channel(logging_channel_id[key])
            if channel:
                embed.add_field(
                    name=f"{key} 日誌頻道",
                    value=f"{channel.mention}",
                    inline=False,
                )
        embed.color = (
            discord.Color.green() if is_logging_enabled else discord.Color.red()
        )
        await itat.followup.send(embed=embed, ephemeral=True)

    @server_logger.command(
        name="ignore_channel", description="新增/移除日誌忽略記錄的頻道"
    )
    @app_commands.guild_install()
    async def set_ignore_channel(
        self, itat: discord.Interaction, channel: discord.TextChannel
    ):
        guild_id = itat.guild_id
        data = db_handler.get(query={"_id": guild_id})
        if data:
            ignore_list = (
                data[0]
                .get("settings", {})
                .get("logging_channel_id", {})
                .get("ignore", [])
            )
        else:
            ignore_list = []

        if channel.id in ignore_list:
            ignore_list.remove(channel.id)
        else:
            ignore_list.append(channel.id)

        db_handler.update_one(
            query={"_id": guild_id},
            new_values={"settings.logging_channel_id.ignore": ignore_list},
            upsert=True,
        )

        await itat.response.send_message(
            f"已忽略紀錄 {channel.mention} 的變化", ephemeral=True
        )

    @server_logger.command(name="set_log_channel", description="設定伺服器日誌的頻道")
    @app_commands.choices(
        logging_type=[
            app_commands.Choice(name="預設", value="default"),
            app_commands.Choice(name="成員", value="member"),
            app_commands.Choice(name="文字訊息", value="message"),
            app_commands.Choice(name="伺服器", value="server"),
            app_commands.Choice(name="語音", value="voice"),
            app_commands.Choice(name="加入/離開", value="join/leave"),
        ]
    )
    @app_commands.guild_install()
    async def set_log_channel(
        self,
        itat: discord.Interaction,
        channel: discord.TextChannel,
        logging_type: app_commands.Choice[str],
    ):
        guild_id = itat.guild_id
        data = db_handler.get(query={"_id": guild_id})
        if data:
            data = data[0]
        old_channel_id = (
            data.get("settings", {})
            .get("logging_channel_id", {})
            .get(logging_type.value, None)
        )
        # 於忽略列表中移除舊的預設頻道
        if old_channel_id:
            ignore_list = Utils.get_ignore_list(guild_id)
            if old_channel_id in ignore_list:
                ignore_list.remove(old_channel_id)
                db_handler.update_one(
                    query={"_id": guild_id},
                    new_values={"settings.logging_channel_id.ignore": ignore_list},
                    upsert=True,
                )
        # 設定新的預設頻道
        db_handler.update_one(
            query={"_id": guild_id},
            new_values={
                f"settings.logging_channel_id.{logging_type.value}": channel.id
            },
            upsert=True,
        )
        Utils.ignore_channel(guild_id, channel.id)

        logger.info(
            f"Set {logging_type.value} logging channel for guild: {itat.guild.name}-{guild_id} to channel: {channel.name}-{channel.id}"
        )
        await itat.response.send_message(
            f"{logging_type.name}伺服器日誌頻道已設定為 {channel.mention}。",
            ephemeral=True,
        )
