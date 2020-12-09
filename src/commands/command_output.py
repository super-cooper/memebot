import io
from typing import Union, KeysView, ValuesView, List, Optional

import discord


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

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __repr__(self) -> str:
        return "CommandOutput(" + " ".join(f"{key}={repr(self.kwargs[key])}" for key in self.kwargs.keys()) + ")"

    def set_content(self, content: str) -> 'CommandOutput':
        """
        Adds content to a message being sent to discord. This can plainly be regarded as
        a regular text message
        :param content: The text to be added to the output
        :return: self
        """
        self.kwargs[CommandOutput.CONTENT] = content
        return self

    def set_text(self, text: str) -> 'CommandOutput':
        """
        Wrapper method for add_content just in case the name isn't clear
        :param text: The text to send
        :return: self
        """
        return self.set_content(text)

    def append_line(self, text: str) -> 'CommandOutput':
        """
        Appends a newline, and then the provided text to the content section of this output. If this output's content
        section is currently empty, a newline will not be added.
        :param text: The text to append
        :return: self
        """
        if len(self.kwargs[CommandOutput.CONTENT]) > 0:
            self.kwargs[CommandOutput.CONTENT] += f"\n{text}"
            return self
        else:
            return self.set_content(text)

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
        :param spoiler: Tells whether the file should be spoiler'd (Default: False)
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
