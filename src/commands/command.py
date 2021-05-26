from abc import abstractmethod
from typing import List, Type

import discord

from commands.command_output import CommandOutput
from lib import status


class CommandMeta(type):
    """
    Metaclass that establishes appropriate relationships to other commands
    """

    def __init__(cls, name, bases, dct) -> None:
        super().__init__(cls)
        if cls.__name__ == "Command":
            cls.parent: None
        else:
            cls.parent: Command = Command(name="default", description="", long_description="")
        cls.subcommands: List[Command] = []


class Command(metaclass=CommandMeta):
    """
    Defines a base command. This class itself should never be instantiated, but MUST be implemented by every command
    used by Memebot. Each Comamnd has a required set of attributes:

        - name: this is the activator for the command, i.e. the thing used like `!name`
        - description: this is a brief description of the command, used by !help
        - long_description: this is a longer description of the command which gives the user more context about its use
    """

    @abstractmethod
    def __init__(self, name: str = None, description: str = None, long_description: str = None, example_args: str = ""):
        """
        Default constructor. Ensures that all pieces of command are properly implemented.
        Default values are used for required arguments so that subclasses are able to override this method without
        requiring the arguments.
        :param name: The name of the command, which is the "activation string" when typed by a user in Discord.
        :param description: A _very_ brief description of the command to be printed by the !help command.
        :param long_description: a long description with more context about the command's use
        :param example_args: An example of arguments to be used with this command, to be printed as a usage message.
        :raise ValueError: if a required attribute is not set or is invalid.
        """
        if name is None:
            raise ValueError(f"Every command needs to have a name! ({type(self).__name__})")
        if not (name.islower() and name.isalpha()):
            raise ValueError(f"Command names must be a single word, all lowercase! ({name})")
        self.name: str = name
        if description is None:
            raise ValueError(f"Every command needs to have a description! ({type(self).__name__})")
        if long_description is None:
            raise ValueError(f"Every command needs to have a long description! ({type(self).__name__}")
        self.description: str = description
        self.long_description = long_description
        self.example_args: str = example_args
        self.requires_database: bool = False

    def __repr__(self) -> str:
        return f"Command: {type(self).__name__}(name={self.name} description={self.description})"

    def help_text(self) -> CommandOutput:
        """
        Creates useful information to help the user understand the command. By default, combines the Command's
        long_description with usage information.
        :return: a CommandOutput object containing the above information
        """
        parent_list = []
        current_parent = self.parent
        while type(current_parent) is not Command:
            parent_list.append(current_parent.name)
            current_parent = current_parent.parent
        cmd_preamble = ' '.join(parent_list)
        if len(cmd_preamble) > 0:
            cmd_preamble += ' '
        output = CommandOutput(content=self.long_description).append_line(
            f"**`!{cmd_preamble}{self.name}" + (f" {self.example_args}`**" if len(self.example_args) > 0 else "`**"))
        if self.subcommands:
            output.append_line("").append_line('\n'.join(
                f"`!{self.name} {sub.name} {sub.example_args}`: {sub.description}" for sub in self.subcommands))
        return output

    def fail(self, additional_info: str = "") -> CommandOutput:
        """
        Default behavior for when a command fails. Combines this Command's help_text with additional_info, and sets
        the output's status to FAIL.
        Any overrides of this method are permitted to behave in whatever way desired, and may return whatever
        information desired, at discretion of the developer.
        :return: Information to be presented to the server upon failure of this command.
        """
        output = self.help_text()
        if additional_info:
            output.append_line("").append_line(additional_info)
        output.status = status.FAIL
        return output

    @abstractmethod
    async def exec(self, args: List[str], message: discord.Message) -> CommandOutput:
        """
        Executes the command.
        :param args: The arguments passed to the command
        :param message: The raw Discord Message object for extracting metadata
        :return: a CommandOutput object that will be posted to Discord
        """
        raise NotImplementedError()

    async def callback(self, *args, **kwargs) -> None:
        """
        Provide a callback function for the command to run after the initial response is created. This callback is run
        after the first response (i.e. the return value of Command.exec) is sent to the server.
        """
        pass


class has_subcommands:
    """
    Modifies a command's constructor such that it will register itself and all subcommands when instantiated
    """

    def __init__(self, *subcommands: Type[Command]) -> None:
        self.subcommands = subcommands

    def __call__(self, cmd: Type[Command]):
        original_init = cmd.__init__

        def __init__(inner_self):
            original_init(inner_self)
            for sub in self.subcommands:
                sub.parent = inner_self
                cmd.subcommands.append(sub())

        cmd.__init__ = __init__

        return cmd
