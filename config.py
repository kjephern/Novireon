import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(PROJECT_ROOT, "data", "GenSenRounded2-M.ttc")
DISCORD_DEFAULT_AVATAR = os.path.join(
    PROJECT_ROOT, "data", "default_discord_user_avatar.png"
)
DEFAULT_AVATAR = os.path.join(PROJECT_ROOT, "data", "default_avatar.jpg")


class MusicConfig:
    PLAYABACK_STATE_UPDATER_INTERVAL = 5  # seconds
    MAX_SONGS_ADD_VIA_PLAYLIST = 20
    MAX_SHOWED_SONGS_IN_LIST_QUEUE = 10  # recommend <=20
    ADD_TO_QUEUE_COLOR = 0x28FF28
    LIST_QUEUE_COLOR = 0xFFCF40
    PLAYING_COLOR = 0xADC8FF
