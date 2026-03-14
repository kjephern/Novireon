import asyncio
import discord
import logging
import re
import subprocess
import time
import urllib.parse

from mongo_crud import MongoCRUD
from pymongo import MongoClient

from Novireon.src.util.config import get_config

logger = logging.getLogger("player.utils")
logger.setLevel(logging.INFO)
player_config = get_config("Player")

mongo_client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=15000)

db_handler = MongoCRUD(
    client=mongo_client,
    db_name="Norvireon_bot_db",
    collection_name="Player_data",
    logger=logger,
)


def format_time(seconds):
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(int(mins), 60)
    return f"{hours}:{mins:02}:{secs:02}" if hours > 0 else f"{mins}:{secs:02}"


def generate_progress_bar(guild_id: int) -> str:
    """to generate a playback progress bar

    Args:
        guild_id (int): the guild's id that is playing

    Returns:
        str: The progress bar
    """
    data = db_handler.get(query={"_id": guild_id})[0]
    is_playing = data.get("is_playing")
    is_live = data["current_playing"].get("is_live", False)
    start_time = data["start_time"]
    duration = data["current_playing"].get("duration", None)
    total_paused_duration = data["total_paused_duration"]
    if is_live:
        return "直播中"
    if total_paused_duration is None:
        total_paused_duration = 0

    if not is_playing:
        pause_time = data.get("pause_time", start_time)
        elapsed = int(pause_time - start_time - total_paused_duration)
    else:
        elapsed = int(time.time() - start_time - total_paused_duration)
    progress = min(elapsed / duration, 1.0)
    length = 20
    filled_length = int(length * progress)
    bar = "─" * filled_length + "•" + "─" * (length - filled_length - 1)

    if is_playing:
        return f"播放中\n`[{bar}]` `({format_time(elapsed)}/{format_time(duration)})`"
    else:
        return f"已暫停\n`[{bar}]` `({format_time(elapsed)}/{format_time(duration)})`"


def get_source_name(url: str) -> str:
    """Get where the source of the url is

    Args:
        url (str): The source URL

    Returns:
        str: Source
    """
    if not isinstance(url, str):
        return ""

    parsed = urllib.parse.urlparse(url)
    hostname = parsed.hostname

    if not hostname:
        return ""

    hostname = hostname.lower()

    rules = {
        "youtube": ("youtube.com", "youtu.be"),
        "monster_siren": ("monster-siren.hypergryph.com",),
        "spotify": ("open.spotify.com",),
    }

    for source_name, domains in rules.items():
        if hostname.endswith(domains):
            return source_name
    audio_extensions = [".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"]
    pattern = "|".join(map(re.escape, audio_extensions))

    if re.search(pattern, url):
        return "direct_audio"
    return ""


async def get_web_audio_duration(url: str) -> int:
    """get web audio duration

    Args:
        url (str): The web audio URL

    Returns:
        int: The duration of the web audio in seconds.
    """
    FFPROBE_PATH = "ffprobe"
    args = [
        FFPROBE_PATH,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        "-i",
        url,
    ]

    try:
        process = await asyncio.create_subprocess_exec(*args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            logging.error(f"FFprobe error: {stderr.decode('utf-8')}")
            return 0

        duration_str = stdout.decode("utf-8").strip()
        if not duration_str:
            return 0

        return round(float(duration_str))

    except Exception as e:
        logging.error(f"Error getting duration: {e}")
        return 0


def is_valid_url(url):
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def return_to_default_player_settings(guild_id):
    try:
        data = db_handler.get(query={"_id": guild_id})
        if data:
            played = data[0].get("played", [])
        else:
            played = []
        db_handler.update_many(
            query={"_id": guild_id},
            new_values={
                "current_playing": {},
                "is_playing": False,
                "is_live": False,
                "if_recommend": False,
                "played": played[-50:],
                "queue": [],
                "pause_time": None,
                "start_time": None,
                "total_paused_duration": 0,
            },
        )
        logger.info("returned to default player settings.")
    except Exception as e:
        logger.critical(f"Can not return to default player settings!\n{e}")


def create_queue_embed(data: dict) -> discord.Embed:
    """creat an embed for new item in queue

    Args:
        data (dict): {title, author, duration, song_url, thumbnail, is_live, requester}

    Returns:
        discord.Embed: The embed
    """
    title = data.get("title", "Unknown Title")
    thumbnail = data.get("thumbnail", None)
    duration = data.get("duration", None)
    author = data.get("author", "Unknown Artist")
    embed = discord.Embed(
        color=player_config["colors.add_to_queue"],
        title=f"加入佇列:\n{title}",
        description=f"by {author}",
    )
    embed.add_field(
        name="時長",
        value="直播" if data.get("is_live", False) else format_time(duration),
    )

    embed.add_field(name="\u200b", value=f"由{data.get('requester', 'Unknown User')}加入")
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    return embed
