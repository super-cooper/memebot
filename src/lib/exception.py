import discord.ext.commands


class MemebotUserError(discord.ext.commands.CommandError):
    """
    Exception which carries a message to be displayed to the user
    """


class MemebotInternalError(discord.ext.commands.CommandError):
    """
    Exception which is thrown on purpose, but whose content would likely confuse a user.
    """
