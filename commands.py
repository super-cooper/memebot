import datetime
import io
from collections import defaultdict
from string import ascii_lowercase as alphabet
from typing import List, Callable, Union, ValuesView, KeysView

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
    def get_command_by_name(command: str) -> Callable[[List[str]], 'CommandOutput']:
        """
        Backbone of the command interface. Entries should be formatted as: ::

            '!command': function

        The function should be defined further down in this class as a static method.
        All functions must take in only a list of strings as their argument,
        and return a dictionary which represents keyword argument pairs to be used by
        channel.send()

        :return: A function that executes the requested command
        """
        return defaultdict(lambda: Commands.help, {
            '!hello': Commands.hello,
            '!poll': Commands.poll
        })[command]

    @staticmethod
    def help(args: List[str]) -> 'CommandOutput':
        """
        Default command, lists all possible commands and a short description of each.
        :param args: Ignored
        :return: A formatted list of all commands
        """
        return CommandOutput().add_text("""Commands:
        `!help`  - Runs this command
        `!hello` - Prints "Hello!"
        `!poll`  - Runs a simple poll""")

    @staticmethod
    def hello(args: List[str]) -> 'CommandOutput':
        """
        Prints "Hello!" on input "!hello"
        :param args: ignored
        :return: The string "Hello!"
        """
        return CommandOutput().add_text("Hello!")

    @staticmethod
    def poll(args: List[str]) -> 'CommandOutput':
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

        return CommandOutput().add_embed(embed)

    @staticmethod
    def execute(command: str, args: List[str], client: discord.Client = None) -> 'CommandOutput':
        """
        Executes the command with the given args
        :param command: The !command to execute
        :param args: The arguments for the command
        :param client: The Discord client being used (MemeBot)
        :return: The result of running command with args, formatted as a CommandOutput object to be sent to Discord
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


class CommandOutput:
    """
    A class to standardize building a command output. Methods correspond to
    kwargs in discord.message.message.channel.send()
    """
    CONTENT = 'content'
    EMBED = 'embed'
    TTS = 'tts'
    FILE = 'file'
    FILES = 'files'
    LIFETIME = 'delete_after'
    NONCE = 'nonce'

    def __init__(self, kwargs: dict = None):
        if type(kwargs) is dict:
            self.kwargs = kwargs
        else:
            # dict to hold keyword arguments
            self.kwargs = {}

    def add_content(self, content: str) -> 'CommandOutput':
        """
        Adds content to a message being sent to discord. This can plainly be regarded as
        a regular text message
        :param content: The text to be added to the output
        :return: self
        """
        self.kwargs[CommandOutput.CONTENT] = content
        return self

    def add_text(self, text: str) -> 'CommandOutput':
        """
        Wrapper method for add_content just in case the name isn't clear
        :param text: The text to send
        :return: self
        """
        return self.add_content(text)

    def add_embed(self, embed: discord.Embed) -> 'CommandOutput':
        """
        Adds an embed to a message being sent to discord
        :param embed: The embed object to add to the message
        :return: self
        """
        self.kwargs[CommandOutput.EMBED] = embed
        return self

    def set_tts(self, tts: bool = True) -> 'CommandOutput':
        """
        Enables or disables text-to-speech for a message being sent to discord
        :param tts: Tells if the content of this message will be read aloud (Default: True)
        :return: self
        """
        self.kwargs[CommandOutput.TTS] = tts
        return self

    def add_file(self, file: Union[str, io.BufferedIOBase], file_name: str = None,
                 spoiler: bool = False) -> 'CommandOutput':
        """
        Adds a file to a message that is being sent to discord
        :param file: The file being sent. Can either be a path (string) or file-like object (io.BufferedIOBase)
        :param file_name: An optional, alternate name to the file
        :param spoiler: Tells whether or not the file should be spoiler'd (Default: False)
        :return: self
        """
        self.kwargs[CommandOutput.FILE] = discord.File(fp=file, filename=file_name, spoiler=spoiler)
        return self

    def add_files(self, files: List[Union[str, io.BufferedIOBase]]) -> 'CommandOutput':
        """
        Adds multiple files at once to a message being sent to Discord. !! Maximum of 10 files !!
        :param files: list of file paths or file-like objects
        :return: self
        :raises ValueError if there is an attempt to add more than 10 files to the output
        """
        # check if, after this operation, there will be more than 10 files in the message
        total_files = (len(self.kwargs[CommandOutput.FILES]) if CommandOutput.FILES in self.kwargs else 0) + len(files)
        if total_files > 10:
            raise ValueError(f"Cannot send more than 10 files! (tried to send total of {total_files}")
        # if there are no files stored in the output, initialize it in the kwargs dict
        if total_files == len(files):
            self.kwargs[CommandOutput.FILES] = []
        self.kwargs[CommandOutput.FILES] += files
        return self

    def set_time_to_delete(self, time_to_delete: float) -> 'CommandOutput':
        """
        Wrapper for set_lifetime()
        :param time_to_delete: The time (in seconds) after which this message will be deleted after sending
        :return: self
        """
        return self.set_lifetime(time_to_delete)

    def set_lifetime(self, lifetime: float) -> 'CommandOutput':
        """
        Sets the output to expire (be deleted) a certain time after being posted
        :param lifetime: The expiration time of this message, in seconds
        :return: self
        """
        self.kwargs[CommandOutput.LIFETIME] = lifetime
        return self

    def __str__(self) -> str:
        return str(self.kwargs)

    def __contains__(self, item: str) -> bool:
        return item in self.kwargs

    def __add__(self, other: 'CommandOutput') -> 'CommandOutput':
        return CommandOutput(self.kwargs.update(other.kwargs))

    def keys(self) -> KeysView[str]:
        return self.kwargs.keys()

    def values(self) -> ValuesView:
        return self.kwargs.values()
