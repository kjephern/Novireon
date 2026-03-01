import discord
import os
import pytz

from datetime import datetime
from discord import Message, Member, Embed, Color, User
from discord.ext import commands
from typing import Literal

from Novireon.cogs.ServerLogger.utils import *

import logging

logger = logging.getLogger("server_logger.main")
logger.setLevel(logging.INFO)

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


class ServerLoggerMain:
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    async def message_event(self, before: Message, after: Message, event_type: str):
        if after:
            message = after
        else:
            return
        guild_id = message.guild.id
        if not is_logging_enabled(guild_id):
            return
        channel_id = message.channel.id
        ignore_list = get_ignore_list(guild_id)
        if channel_id in ignore_list:
            return
        channel = await self.get_logging_channel(guild_id, "message")
        embed = Embed()
        embed.set_author(
            url=message.author.display_avatar.url,
            name=message.author.display_name,
        )
        embed.set_thumbnail(url=message.author.display_avatar.url)
        embed.add_field(
            name="原始訊息",
            value=before.content if before else "無法獲取訊息",
            inline=False,
        )
        match event_type:
            case "edit":
                embed.title = f"訊息在 {message.jump_url} 被編輯"
                embed.color = Color.blue()
                embed.add_field(
                    name="編輯後訊息",
                    value=after.content or "無法獲取訊息",
                    inline=False,
                )
            case "delete":
                embed.title = f"訊息在 {before.jump_url} 被刪除"
                embed.color = Color.red()
        taipei_tz = pytz.timezone("Asia/Taipei")
        current_time = datetime.now().timestamp()
        embed.set_footer(
            text=f"Message ID: {message.id}\nEdited at {datetime.fromtimestamp(current_time,tz=taipei_tz).strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await channel.send(embed=embed, silent=True)
        return

    async def member_event(self, before: Member, after: Member, event_type: str):
        guild_id = after.guild.id

        if not is_logging_enabled(guild_id):
            return
        channel = await self.get_logging_channel(guild_id, "member")
        embed = Embed()
        embed.set_author(
            icon_url=after.display_avatar.url,
            name=after.display_name,
        )
        embed.set_thumbnail(url=after.display_avatar.url)
        match event_type:
            case "nick":
                embed.title = f"暱稱更改"
                embed.add_field(name="\u200b", value=after.mention, inline=False)
                embed.color = Color.blue()
                embed.add_field(
                    name="更改前暱稱",
                    value=before.nick or before.name,
                    inline=False,
                )
                embed.add_field(
                    name="更改後暱稱",
                    value=after.nick or "無暱稱",
                    inline=False,
                )
            case "role":
                before_roles = set(before.roles)
                after_roles = set(after.roles)
                added_roles = after_roles - before_roles
                removed_roles = before_roles - after_roles
                embed.title = f"身分組變更"
                embed.add_field(name="\u200b", value=after.mention, inline=False)
                embed.color = Color.purple()
                if added_roles:
                    embed.add_field(
                        name=f"新增身分組",
                        value="\n".join([role.mention for role in added_roles if role.is_default() is False]),
                        inline=False,
                    )
                    if not removed_roles:
                        embed.color = Color.green()
                if removed_roles:
                    embed.add_field(
                        name=f"移除身分組",
                        value="\n".join([role.mention for role in removed_roles if role.is_default() is False]),
                        inline=False,
                    )
                    if not added_roles:
                        embed.color = Color.red()
        taipei_tz = pytz.timezone("Asia/Taipei")
        current_time = datetime.now().timestamp()
        embed.set_footer(
            text=f"Member ID: {after.id}\nUpdated at {datetime.fromtimestamp(current_time,tz=taipei_tz).strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await channel.send(embed=embed, silent=True)
        return

    async def user_event(self, before: User, after: User, event_type: str):
        guilds = after.mutual_guilds
        channels = []
        for guild in guilds:
            guild_id = guild.id
            if not is_logging_enabled(guild_id):
                return
            channel = await self.get_logging_channel(guild_id, "member")
            if channel is None:
                pass
            channels.append(channel)
        if not channels:
            return
        embed = Embed()
        embed.set_author(
            icon_url=after.display_avatar.url,
            name=after.display_name,
        )
        embed.set_thumbnail(url=after.display_avatar.url)
        match event_type:
            case "avatar":
                embed.title = f"頭像更改"
                embed.add_field(name="\u200b", value=after.mention, inline=False)
                embed.color = Color.yellow()
                embed.set_image(url=after.display_avatar.url)
            case "global_name":
                embed.title = f"顯示名稱更改"
                embed.add_field(name="\u200b", value=after.mention, inline=False)
                embed.color = Color.blue()
                embed.add_field(
                    name="更改前顯示名稱",
                    value=before.global_name,
                    inline=False,
                )
                embed.add_field(
                    name="更改後顯示名稱",
                    value=after.global_name,
                    inline=False,
                )
            case "username":
                embed.title = f"使用者名稱更改"
                embed.color = Color.green()
                embed.add_field(name="\u200b", value=after.mention, inline=False)
                embed.add_field(
                    name="更改前使用者名稱",
                    value=before.name,
                    inline=False,
                )
                embed.add_field(
                    name="更改後使用者名稱",
                    value=after.name,
                    inline=False,
                )
            case "discriminator":
                embed.title = f"自述更改"
                embed.add_field(name="\u200b", value=after.mention, inline=False)
                embed.color = Color.orange()
                embed.add_field(
                    name="更改前自述",
                    value=before.discriminator,
                    inline=False,
                )
                embed.add_field(
                    name="更改後自述",
                    value=after.discriminator,
                    inline=False,
                )
        taipei_tz = pytz.timezone("Asia/Taipei")
        current_time = datetime.now().timestamp()
        embed.set_footer(
            text=f"Member ID: {after.id}\nUpdated at {datetime.fromtimestamp(current_time,tz=taipei_tz).strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await channel.send(embed=embed, silent=True)
        return

    async def get_logging_channel(self, guild_id: int, type: Literal["message", "member"]):
        data = db_handler.get(query={"_id": guild_id})
        if not data:
            return
        logging_channel_id = data[0].get("settings", {}).get("logging_channel_id", {})
        if type in logging_channel_id:
            channel_id = logging_channel_id[type]
        else:
            channel_id = logging_channel_id.get("default")
        if channel_id is None:
            return
        if channel_id:
            channel: discord.TextChannel = self.bot.get_channel(channel_id)
            if channel is None:
                channel = await self.bot.fetch_channel(channel_id)
        if channel is None:
            return
        else:
            return channel
