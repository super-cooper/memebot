import datetime
from collections import defaultdict
from string import ascii_lowercase as alphabet
from typing import List, DefaultDict, Callable

import discord

import constants


# noinspection PyUnusedLocal
class Commands:
    """
    Manages all user-facing commands. The reason this is done as a class instead of just loose functions is so that
    the commands() method can be near the top of the file, so programmers remember to add their command to the
    dictionary. If this causes enough ire, it can easily be refactored.
    """

    @staticmethod
    def commands() -> DefaultDict[str, Callable[[List[str]], str]]:
        """
        Backbone of the command interface. Entries should be formatted as: ::

            '!command': function

        The function should be defined further down in this class as a static method.
        All functions must take in only a list of strings as their argument,
        and return only a single string, or a discord.Embed object.

        :return: A dictionary mapping all commands to their functions
        """
        return defaultdict(lambda: Commands.help, {
            '!hello': Commands.hello,
            '!poll': Commands.poll
        })

    @staticmethod
    def help(args: List[str]) -> str:
        """
        Default command, lists all possible commands and a short description of each.
        :param args: Ignored
        :return: A formatted list of all commands
        """
        return """Commands:
        `!help`  - Runs this command
        `!hello` - Prints "Hello!"
        `!poll`  - Runs a simple poll
        """

    @staticmethod
    def hello(args: List[str]) -> str:
        """
        Prints "Hello!" on input "!hello"
        :param args: ignored
        :return: The string "Hello!"
        """
        return "Hello!"

    @staticmethod
    def poll(args: List[str]) -> discord.Embed:
        question, *options = args
        embed = discord.Embed(
            title=':bar_chart: **New Poll!**',
            description=f'_{question}_',
            color=constants.COLOR,
            timestamp=datetime.datetime.utcnow()
        )
        for i in range(len(options)):
            embed.add_field(name=f':regional_indicator_{alphabet[i]}:', value=options[i])
        if len(options) < 2 or options in (['yes', 'no'], ['no', 'yes'], ['yea', 'nay']):
            embed.add_field(name=':thumbsup:', value=':)').add_field(name=':thumbsdown:', value=':(')
        return embed
