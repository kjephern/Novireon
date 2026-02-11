import discord
import logging
import time
import urllib.parse

from mongo_crud import MongoCRUD
from pymongo import MongoClient

from config.Music_config import ADD_TO_QUEUE_COLOR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("music.utils")

mongo_client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=15000)

db_handler = MongoCRUD(
    client=mongo_client,
    db_name="Norvireon_bot_db",
    collection_name="Music_data",
    logger=logger,
)


def format_time(seconds):
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(int(mins), 60)
    return f"{hours}:{mins:02}:{secs:02}" if hours > 0 else f"{mins}:{secs:02}"


def generate_progress_bar(guild_id):
    data = db_handler.get(query={"_id": guild_id})[0]
    is_playing = data.get("is_playing")
    start_time = data["start_time"]
    duration = data["current_playing"]["duration"]
    total_paused_duration = data["total_paused_duration"]
    author = data.get("author", "Unknown Artist")
    if duration == 0:
        return ""
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


def get_source_name(url):
    if not isinstance(url, str):
        return ""
    hostname = urllib.parse.urlparse(url).hostname
    if hostname:
        if "youtube.com" in hostname or "youtu.be" in hostname:
            return "youtube"
        if "monster-siren.hypergryph.com" in hostname:
            return "monster_siren"
    return ""


def is_valid_url(url):
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def return_to_default_music_settings(guild_id):
    try:
        db_handler.update_one(
            query={"_id": guild_id},
            new_values={
                "current_playing": {},
                "embed_message_id": None,
                "is_playing": False,
                "if_recommend": False,
                "played": [],
                "queue": [],
            },
            upsert=True,
        )
        logger.info("returned to default music settings.")
    except Exception as e:
        logger.critical(f"Can not return to default music settings!")


def create_queue_embed(data: dict) -> discord.Embed:
    title = data.get("title", "Unknown Title")
    thumbnail = data.get("thumbnail", "")
    duration = data.get("duration", 0)
    author = data.get("author", "Unknown Artist")
    embed = discord.Embed(
        color=ADD_TO_QUEUE_COLOR,
        title=f"加入佇列:\n{title}",
        description=f"by {author}",
    )
    embed.add_field(name="時長", value=format_time(duration))

    embed.add_field(
        name="\u200b", value=f"由{data.get('requester', 'Unknown User')}加入"
    )
    embed.set_thumbnail(url=thumbnail)
    return embed
