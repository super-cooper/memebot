from abc import abstractmethod
from typing import List, Callable, Union, Tuple

import discord

from commands.command_output import CommandOutput


class Command:
    """
    Defines a base command. This class itself should never be instantiated, but MUST be implemented by every command
    used by Memebot. Each Comamnd has a required set of attributes:

        - name: this is the activator for the command, i.e. the thing used like `!name`
        - description: this is a brief description of the command, used by !help
    """

    DEFAULT_NAME = "Command"
    DEFAULT_DESC = "Unknown"

    @abstractmethod
    def __init__(self, name: str = DEFAULT_NAME, description: str = DEFAULT_DESC, example_args: str = ""):
        """
        Default constructor. Ensures that all pieces of command are properly implemented.
        :param name The name of the command, which is the "activation string" when typed by a user in Discord.
        :param description A _very_ brief description of the command to be printed by the !help command.
        :param example_args An example of arguments to be used with this command, to be printed as a usage message.
        :raise ValueError if a required attribute is not set or is invalid.
        """
        if name is None:
            raise ValueError(f"Every command needs to have a name! ({type(self).__name__})")
        if not name.islower() or any(c.isspace() for c in name):
            raise ValueError(f"Command names must be a single word, all lowercase! ({name})")
        self.name: str = name
        if description is None:
            raise ValueError(f"Every command needs to have a description! ({type(self).__name__})")
        self.description: str = description
        self.example_args: str = example_args
        # TODO rushed temporary solution. Perhaps un-self-referential Commands should be rethought entirely...
        self.parent: Union[str, None] = None

    def __repr__(self) -> str:
        return f"Command: {type(self).__name__}(name={self.name} description={self.description})"

    @abstractmethod
    def help_text(self) -> CommandOutput:
        """
        Returns a string of help text for this particular command. Describeds what the command does and how to use it.
        :returns A help message, which should be sent to the server.
        """
        pass

    def fail(self, additional_info: str = "") -> CommandOutput:
        """
        Default behavior for when a command fails. Creates a message that prints information about the command as well
        as how it is used.
        Any overrides of this method are permitted to behave in whatever way desired, and may return whatever
        information desired, at discretion of the developer.
        :return: Information to be presented to the server upon failure of this command.
        """
        output = self.help_text().append_line(
            f"**`!{self.name if self.parent is None else f'{self.parent} {self.name}'}" + (
                f" {self.example_args}`**" if len(self.example_args) > 0 else "`**"))
        if additional_info:
            output.append_line(additional_info)
        return output

    @abstractmethod
    async def exec(self, args: List[str], message: discord.Message) -> \
            Union[CommandOutput, Tuple[CommandOutput, Callable[[discord.Message], None]]]:
        """
        Executes the command.
        :param args: The arguments passed to the command
        :param message: The raw Discord Message object for extracting metadata
        :return: a CommandOutput object that will be posted to Discord
        :return: A callback function that will be called after the output is sent to the server. The function MUST
        accept a discord.Message and only a discord.Message. Any return values will be ignored.
        """
        pass

    def callback(self, *args, **kwargs) -> None:
        pass
