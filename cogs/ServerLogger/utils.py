import logging
import os

from pymongo import MongoClient
from typing import Literal

from mongo_crud import MongoCRUD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("server_logger.utils")

mongo_uri = os.getenv("MONGO_URI")
mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=15000)
db_handler = MongoCRUD(
    client=mongo_client,
    db_name="Norvireon_bot_db",
    collection_name="Server_logger_data",
    logger=logger,
)


def get_ignore_list(guild_id: int):
    data = db_handler.get(query={"_id": guild_id})
    if data:
        ignore_list = data[0].get("settings", {}).get("logging_channel_id", {}).get("ignore", [])
    else:
        ignore_list = []
    return ignore_list


def ignore_channel(guild_id: int, channel_id: int):
    ignore_list = get_ignore_list(guild_id)
    if channel_id not in ignore_list:
        ignore_list.append(channel_id)
        db_handler.update_one(
            query={"_id": guild_id},
            new_values={"settings.logging_channel_id.ignore": ignore_list},
            upsert=True,
        )


def is_logging_enabled(guild_id: int):
    data = db_handler.get(query={"_id": guild_id})
    if not data:
        return
    data = data[0]
    settings = data.get("settings", {})
    return settings.get("is_logging_enabled", False)
