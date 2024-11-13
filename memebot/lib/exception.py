import discord


class MemebotUserError(discord.app_commands.AppCommandError):
    """
    Exception which carries a message to be displayed to the user
    """


class MemebotInternalError(discord.app_commands.AppCommandError):
    """
    Exception which is thrown on purpose, but whose content would likely confuse a user.
    """
