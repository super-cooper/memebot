from collections import defaultdict
from typing import Callable, List, Dict


# noinspection PyUnusedLocal
class Commands:
    """
    Manages all user-facing commands. The reason this is done as a class instead of just loose functions is so that
    the commands() method can be near the top of the file, so programmers remember to add their command to the
    dictionary. If this causes enough ire, it can easily be refactored.
    """

    @staticmethod
    def commands() -> Dict[str, Callable[[List[str]], str]]:
        """
        Backbone of the command interface. Entries should be formatted as: ::

            '!command': function

        The function should be defined further down in this class as a static method.
        All functions should take in only a list of strings as their argument, and return only a single string.

        :return: The function that executes the command
        """
        return defaultdict(lambda: Commands.help, {
            '!hello': Commands.hello
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
        """

    @staticmethod
    def hello(args: List[str]) -> str:
        """
        Prints "Hello!" on input "!hello"
        :param args: ignored
        :return: The string "Hello!"
        """
        return "Hello!"
