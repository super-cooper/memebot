import discord.ext.commands

from .hello import hello
from .paywall import paywall, paywall_context_menu
from .role import role
from .trackers import trackers, trackers_context_menu


def register_commands(bot: discord.ext.commands.Bot) -> None:
    bot.tree.add_command(hello)
    bot.tree.add_command(paywall)
    bot.tree.add_command(paywall_context_menu)
    bot.tree.add_command(role)
    bot.tree.add_command(trackers)
    bot.tree.add_command(trackers_context_menu)
