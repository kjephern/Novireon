# Novireon

Novireon is a versatile Discord bot built with `discord.py`, designed to enhance your server with a range of features from music playback to detailed server event logging. It uses MongoDB for persistent data storage, ensuring settings and queues are saved across sessions.

## Features

*   **🎵 Advanced Music System:**
    *   Play music from YouTube (single videos and playlists) and Monster Siren (Arknights music).
    *   Robust queue system managed in a MongoDB database.
    *   Interactive playback controls (pause, resume, skip, stop) via slash commands and buttons.
    *   Real-time playback progress bar that updates automatically.
    *   Configurable DJ role for managing music playback permissions.

*   **✍️ Comprehensive Server Logging:**
    *   Logs a wide variety of server events to designated channels.
    *   Tracks message edits and deletions.
    *   Monitors member updates including nickname changes, role assignments, avatar updates, and username changes.
    *   Highly configurable: enable/disable logging globally, set specific channels for different event types (e.g., members, messages), and ignore specific channels.

*   **🖼️ Quote Image Generator:**
    *   Create stylish quote images using the `/make_it_a_quote` command.
    *   Generates a visually appealing image with the quote, author's name, and avatar (from a Discord member, custom upload, or default).

*   **⚙️ Utility Commands:**
    *   A detailed `/ping` command that provides real-time stats on API latency, host server CPU/memory usage, and bot process information.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/rexkung1029/Novireon.git
    cd Novireon
    ```

2.  **Install dependencies:**
    This project uses `uv` for package management. You can install the dependencies from the `pyproject.toml` file.
    ```bash
    pip install uv
    uv pip install -r requirements.txt
    ```
    Alternatively, you can install the dependencies manually using pip:
    ```bash
    pip install discord.py google-api-python-client motor pillow psutil pydub pymongo pynacl python-dotenv pytz requests soundfile yt-dlp
    ```

3.  **Configure Environment Variables:**
    Create a `.env` file in the root directory and add the following variables:
    ```env
    DISCORD=YOUR_DISCORD_BOT_TOKEN
    GOOGLE=YOUR_GOOGLE_API_KEY
    MONGO_URI=YOUR_MONGODB_CONNECTION_STRING
    ```
    *   `DISCORD`: Your Discord bot's token.
    *   `GOOGLE`: A Google API key with the YouTube Data API v3 enabled is required for the music search functionality.
    *   `MONGO_URI`: Your connection string for a MongoDB database.

4.  **Run the bot:**
    ```bash
    python bot.py
    ```
    The bot will log in, sync its slash commands, and become operational.

## Command Usage

All commands are implemented as slash commands for easy use.

### Music Commands

*   `/music play <request>`: Plays a song. The request can be a YouTube/Monster Siren URL or a search query.
*   `/music play_playlist <request> [max_results]`: Adds a random selection of songs from a YouTube playlist to the queue. `max_results` defaults to 5, with a maximum of 25.
*   `/music pause`: Pauses the current song.
*   `/music resume`: Resumes playback.
*   `/music skip`: Skips to the next song in the queue.
*   `/music stop`: Stops playback, clears the queue, and disconnects the bot.

### Music Setup (Admin/DJ Permissions)

*   `/music_setup dj_role [role]`: Sets a "DJ" role that can control music playback. If no role is provided, the DJ role is cleared.
*   `/music_setup channel [channel]`: Designates a specific text channel for music commands.

### Server Logger (Admin Permissions)

*   `/server_logger toggle`: Toggles server logging on or off.
*   `/server_logger list_settings`: Displays the current logging configuration.
*   `/server_logger set_log_channel <channel> <logging_type>`: Sets the destination channel for a specific type of log (e.g., messages, members).
*   `/server_logger ignore_channel <channel>`: Adds or removes a channel from the logging ignore list.

### Utility Commands

*   `/ping`: Shows an embed with detailed real-time status of the bot and its host server.
*   `/make_it_a_quote <quote_context> [author_member] [author_text] [custom_avatar]`: Generates a quote image. You can specify the author by tagging a member or providing text, and optionally upload a custom avatar.
