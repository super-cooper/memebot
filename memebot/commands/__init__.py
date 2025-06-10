import discord.ext.commands

from .hello import hello
from .paywall import paywall, paywall_context_menu
from .role import role


def register_commands(bot: discord.ext.commands.Bot):
    bot.tree.add_command(hello)
    bot.tree.add_command(role)
    bot.tree.add_command(paywall)
    bot.tree.add_command(paywall_context_menu)
