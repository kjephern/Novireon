from discord import app_commands


class NotInValidVoiceChannel(app_commands.CheckFailure):
    pass


class NotInValidCommandChannel(app_commands.CheckFailure):
    pass


class NotDJ(app_commands.CheckFailure):
    pass


class TrackNotFound(app_commands.CheckFailure):
    pass
