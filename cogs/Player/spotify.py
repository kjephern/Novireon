import logging
import os
import spotipy

from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

from cogs.Player.errors import TrackNotFound

logger = logging.getLogger("player.spotify").setLevel(logging.INFO)
load_dotenv()
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

if CLIENT_ID and CLIENT_SECRET:
    auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)


class Spotify:
    def get_spotify_song_data(url: str):
        try:
            info = sp.track(url)
            title = info["name"]
            author = info["artists"][0]["name"]
            return f"{title} {author}"
        except:
            raise TrackNotFound
