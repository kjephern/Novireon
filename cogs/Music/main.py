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

            guild_id = itat.guild_id
            if guild_id not in voice_data:
                voice_data[guild_id] = {}
                music_utils.return_to_default_music_settings(guild_id)

            voice_data[guild_id]["music_channel"] = itat.channel
            voice_data[guild_id]["itat"] = itat

            match music_utils.get_source_name(request):
                case "youtube":
                    data = await Youtube.get_data_from_single(request)
                case "monster_siren":
                    data = Monster_siren.get_song_data(request)
                case "":
                    data = await Functions.search(itat, request)
                    if data is None:
                        return
            user = itat.user.nick if itat.user.nick else itat.user.name
            if data is None:
                await itat.followup.send(
                    "找不到相關的音樂，請嘗試其他關鍵字或網址", ephemeral=True
                )
                return
            else:
                data.update({"requester": user})
                db_handler.append(query={"_id": guild_id}, field="queue", value=data)

            if ("client" not in voice_data[guild_id]) or (
                not voice_data[guild_id]["client"].is_connected()
            ):
                await itat.followup.send("正在處理播放請求", ephemeral=True)
                await Functions._play(guild_id)

            else:
                embed = music_utils.create_queue_embed(data)
                await itat.channel.send(embed=embed)

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
            if max_results < 1:
                max_results = 1
            elif max_results > MAX_SONG_COUNT_ADD_VIA_PLAYLIST:
                max_results = MAX_SONG_COUNT_ADD_VIA_PLAYLIST

            await itat.response.send_message("處理中", ephemeral=True)

            guild_id = itat.guild_id
            if guild_id not in voice_data:
                voice_data[guild_id] = {}
                music_utils.return_to_default_music_settings(guild_id)

            voice_data[guild_id]["music_channel"] = itat.channel
            voice_data[guild_id]["itat"] = itat

            metadatas = await Youtube.get_playlist_metadata(request)
            if metadatas is None:
                await itat.followup.send(
                    "找不到相關的播放列表，請嘗試其他關鍵字或網址", ephemeral=True
                )
                return
            max_songs_count = min(
                max_results,
                len(metadatas),
                MAX_SONG_COUNT_ADD_VIA_PLAYLIST,
            )
            if if_shuffle:
                selected_songs = random.sample(
                    metadatas,
                    max_songs_count,
                )
            else:
                selected_songs = metadatas[:max_songs_count]

            user = itat.user.nick if itat.user.nick else itat.user.name
            for song in selected_songs:
                try:
                    data = await Youtube.get_data_from_single(song["webpage_url"])
                    data.update({"requester": user})
                    db_handler.append(
                        query={"_id": guild_id}, field="queue", value=data
                    )
                    embed = music_utils.create_queue_embed(data)
                    await itat.channel.send(embed=embed)
                    await asyncio.sleep(1)
                except Exception as e:
                    await itat.channel.send(
                        "加入播放列表時發生錯誤，部分歌曲可能未加入佇列。"
                    )
                    logger.error(f"Error adding song from playlist: {e}")
                    continue

            if ("client" not in voice_data[guild_id]) or (
                not voice_data[guild_id]["client"].is_connected()
            ):
                await itat.followup.send("正在處理播放請求", ephemeral=True)
                await Functions._play(guild_id)

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
