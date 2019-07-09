import datetime
from collections import defaultdict
from string import ascii_lowercase as alphabet
from typing import List, Callable, Union

import discord

from lib import constants


# noinspection PyUnusedLocal
class Commands:
    """
    Manages all user-facing commands. The reason this is done as a class instead of just loose functions is so that
    the commands() method can be near the top of the file, so programmers remember to add their command to the
    dictionary. If this causes enough ire, it can easily be refactored.
    """

    client: discord.Client = None

    @staticmethod
    def get_command_by_name(command: str) -> Callable[[List[str]], str]:
        """
        Backbone of the command interface. Entries should be formatted as: ::

            '!command': function

        The function should be defined further down in this class as a static method.
        All functions must take in only a list of strings as their argument,
        and return only a single string, or a discord.Embed object.

        :return: A function that executes the requested command
        """
        return defaultdict(lambda: Commands.help, {
            '!hello': Commands.hello,
            '!poll': Commands.poll
        })[command]

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
        emojis = []
        if len(options) < 2 or options in (['yes', 'no'], ['no', 'yes'], ['yea', 'nay']):
            embed.add_field(name=':thumbsup:', value=':)' if len(options) < 1 else options[0]).add_field(
                name=':thumbsdown:', value=':(' if len(options) < 2 else options[1])
            emojis = [':thumbsup:', ':thumbsdown:']
        else:
            for i in range(len(options)):
                emoji = f':regional_indicator_{alphabet[i]}:'
                embed.add_field(name=emoji, value=options[i])
                emojis.append(emoji)

        # create side effect to react to poll after it is posted
        async def react(message: discord.Message):
            for emote in emojis:
                await message.add_reaction(constants.EMOJI_MAP[emote])

        SideEffects.task = react

        return embed

    @staticmethod
    def execute(command: str, args: List[str], client: discord.Client = None) -> Union[str, discord.Embed]:
        """
        Executes the command with the given args
        :param command: The !command to execute
        :param args: The arguments for the command
        :param client: The Discord client being used (MemeBot)
        :return: The result of running command with args
        """
        if Commands.client is None:
            if client is None:
                raise ValueError("The Commands module does not have access to a client!")
            else:
                Commands.client = client
        return Commands.get_command_by_name(command)(args)


class SideEffects:
    """
    This is a class for when a command needs extra information from the Discord client after
    the command has already been run (to execute certain operations from "beyond the grave"
    Since commands are asynchronous, this works by having the command leave a little job
    in the ``task`` variable. Upon returning control to memebot and sending the output of
    the command to Discord, memebot will send over any possibly needed data through the
    ``borrow()`` function, which will then trigger the execution of ``task``.

    I am going to guess this is a temporary measure, and there is probably a much better way
    to do this.
    """
    task = None

    @staticmethod
    async def borrow(message: discord.Message):
        if SideEffects.task is not None:
            await SideEffects.task(message)
        SideEffects.task = None
