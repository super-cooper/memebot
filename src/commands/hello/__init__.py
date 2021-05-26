from typing import List

import discord

from commands import Command, CommandOutput


class Hello(Command):
    """
    Simple ping command. Say "hello" to Memebot!
    """

    def __init__(self):
        super().__init__(
            name="hello",
            description="Say \"hello\" to Memebot!",
            long_description="A simple ping command. Memebot should respond \"Hello!\""
        )

    async def exec(self, args: List[str], message: discord.Message) -> CommandOutput:
        """
        Prints "Hello!" on input "!hello"
        :param args: ignored
        :param message: ignored
        :return: The string "Hello!"
        """
        author = message.author
        if author is not None:
            # display_name is the nickname if it exists else the username
            msg = f'Hello, {author.display_name}!'
        else:
            msg = 'Hello!'
        return CommandOutput().set_text(msg)
