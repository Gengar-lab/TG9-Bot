"""Contains custom exceptions"""

from discord.ext import commands


class UserNotOwner(commands.CheckFailure):
    """User is not the owner of the bot"""

    def __init__(self):
        self.message = "User is not the owner of the bot!"
        super().__init__(self.message)


class VoiceChError(Exception):
    """Custom Voice Channel error"""

    def __init__(self):
        self.description = "Error while playing music"
        super().__init__(self.description)
