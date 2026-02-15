import asyncio
import discord
import logging
import random
import os

from discord import app_commands
from discord import Interaction as Itat
from discord import VoiceClient as VC
from discord.ext import commands
from pymongo import MongoClient

from mongo_crud import MongoCRUD
from .core import music_utils
from .core.music_checkers import Checkers
from .core.music_data import voice_data
from .core.music_functions import Functions
from .monster_siren import Monster_siren
from .youtube import Youtube

from config.Music_config import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("music.main")

ffmpeg_options = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": '-vn -filter:a "volume=0.3"',
}

mongo_uri = os.getenv("MONGO_URI")
mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=15000)

db_handler = MongoCRUD(
    client=mongo_client,
    db_name="Norvireon_bot_db",
    collection_name="Music_data",
    logger=logger,
)


class MusicMain:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    music = app_commands.Group(
        name="music",
        description="音樂指令",
        allowed_installs=app_commands.AppInstallationType(guild=True, user=False),
    )

    @music.command(name="play", description="播放音樂")
    @app_commands.describe(request="可使用網址或直接搜尋")
    @Checkers.is_in_valid_voice_channel()
    async def command_play(self, itat: Itat, request: str):
        try:
            await itat.response.send_message("處理中", ephemeral=True)
            await Functions.pre_play(itat, request)

        except Exception as e:
            logger.error(f"Command_play Error {e}")
            await itat.followup.send("執行指令時發生錯誤，請稍後再試。", ephemeral=True)

    @music.command(name="play_playlist", description="播放播放列表")
    @app_commands.describe(
        request="僅可使用youtube播放清單網址",
        max_results=f"最多加入幾首歌，預設{DEFAULT_SONG_COUNT_ADD_VIA_PLAYLIST}，最多{MAX_SONG_COUNT_ADD_VIA_PLAYLIST}首",
        if_shuffle="是否以隨機順序加入佇列",
    )
    @Checkers.is_in_valid_voice_channel()
    async def command_play_playlist(
        self,
        itat: Itat,
        request: str,
        max_results: int = DEFAULT_SONG_COUNT_ADD_VIA_PLAYLIST,
        if_shuffle: bool = True,
    ):
        try:
            await Functions.pre_play_playlist(itat, request, max_results, if_shuffle)

        except Exception as e:
            logger.error(f"Command_play_playlist Error {e}")
            await itat.followup.send("執行指令時發生錯誤，請稍後再試。", ephemeral=True)

    @music.command(name="list_queue", description="顯示目前播放佇列")
    @Checkers.is_in_valid_voice_channel()
    async def command_list_queue(self, itat: Itat):
        data = db_handler.get({"_id": itat.guild_id})[0]
        queue = data.get("queue", [])
        if not queue:
            await itat.response.send_message("目前播放佇列為空。", ephemeral=True)
            return
        else:
            embed = discord.Embed(
                color=LIST_QUEUE_COLOR,
                title="目前播放佇列",
            )
            for index, song in enumerate(queue, start=1):
                author = song.get("author", "Unknown Artist")
                title = song.get("title", "Unknown Title")
                duration = song.get("duration", None)
                requester = song.get("requester", "Unknown")
                name = f"{index}. {title}"
                description = (
                    f"by {author} | 直播 | 由{requester}加入"
                    if data.get("is_live", False)
                    else f"by {author} | 時長: {music_utils.format_time(duration)} | 由{requester}加入"
                )
                embed.add_field(
                    name=name[:256],
                    value=description[:1024],
                    inline=False,
                )
                if index >= MAX_SHOWED_SONGS_IN_LIST_QUEUE:
                    embed.add_field(
                        name="\u200b",
                        value=f"...以及其他 {len(queue) - MAX_SHOWED_SONGS_IN_LIST_QUEUE} 首歌曲。\n",
                    )
                    break
            await itat.response.send_message(embed=embed, ephemeral=True)

    @music.command(name="stop", description="停止播放音樂")
    @Checkers.is_dj()
    @Checkers.is_in_valid_voice_channel()
    async def command_stop(self, itat: Itat):
        await itat.response.send_message("處理中", ephemeral=True, delete_after=5)
        guild_id = itat.guild_id
        await Functions._stop(guild_id)

    @music.command(name="skip", description="跳過當前曲目")
    @Checkers.is_dj()
    @Checkers.is_in_valid_voice_channel()
    async def command_skip(self, itat: Itat):
        await itat.response.send_message("處理中", ephemeral=True, delete_after=5)
        guild_id = itat.guild_id
        await Functions._skip(guild_id)

    @music.command(name="pause", description="暫停音樂")
    @Checkers.is_dj()
    @Checkers.is_in_valid_voice_channel()
    async def command_pause(self, itat: Itat):
        await itat.response.send_message("處理中", ephemeral=True, delete_after=5)
        guild_id = itat.guild_id
        await Functions._pause(guild_id)

    @music.command(name="resume", description="繼續播放")
    @Checkers.is_dj()
    @Checkers.is_in_valid_voice_channel()
    async def command_resume(self, itat: Itat):
        await itat.response.send_message("處理中", ephemeral=True, delete_after=5)
        guild_id = itat.guild_id
        await Functions._resume(guild_id)
