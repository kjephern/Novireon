import logging
import os

from discord import app_commands
from discord import Interaction as Itat
from discord import VoiceClient as VC
from pymongo import MongoClient

from .player_data import voice_data
from .player_errors import *
from mongo_crud import MongoCRUD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("player.checkers")


mongo_uri = os.getenv("MONGO_URI")
mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=15000)

db_handler = MongoCRUD(
    client=mongo_client,
    db_name="Norvireon_bot_db",
    collection_name="Player_data",
    logger=logger,
)


class Checkers:
    @staticmethod
    def _is_in_valid_voice_channel(itat: Itat):
        guild_id = itat.guild_id
        if itat.user.voice is None:
            raise NotInValidVoiceChannel
        if guild_id not in voice_data:
            return True
        if "client" not in voice_data[guild_id]:
            return True
        client: VC = voice_data[guild_id]["client"]
        if itat.guild.voice_client is None:
            return True
        return itat.user.voice.channel.id == client.channel.id

    @staticmethod
    def is_in_valid_voice_channel():
        return app_commands.check(Checkers._is_in_valid_voice_channel)

    @staticmethod
    def is_dj():
        return app_commands.check(Checkers._is_dj)

    @staticmethod
    def _is_dj(itat: Itat):
        guild_id = itat.guild_id
        settings = db_handler.get(query={"_id": guild_id})[0]
        dj_role_id = settings.get("dj_role_id", None)

        if itat.user.guild_permissions.administrator:
            return True
        if dj_role_id is None:
            raise NotDJ
        elif dj_role_id is not None:
            if dj_role_id in [role.id for role in itat.user.roles]:
                return True
            else:
                raise NotDJ
