import discord.ext.commands


class MemebotUserError(discord.ext.commands.CommandError):
    """
    Exception which carries a message to be displayed to the user
    """
