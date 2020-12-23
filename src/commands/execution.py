"""
This file contains all the machinery for parsing and executing commands.
"""
import asyncio
import re
import shlex

import discord

from . import registry
from lib import status


async def execute_if_command(message: discord.Message) -> None:
    """
    Attempts to detect if a message is a command and throws it onto the event loop for execution if it is.
    :param message: The message whose content will be parsed
    """
    content = message.content
    if not is_command(content):
        return
    try:
        command, args = registry.parse_command_and_args(shlex.split(prepare_input(message.content)))
    except ValueError as e:
        await message.channel.send('Could not parse command: ' + str(e))
        return

    command_task = asyncio.create_task(command.exec(args, message))
    result = await command_task
    response_task = asyncio.create_task(message.channel.send(**result.kwargs))
    response = await response_task
    # We should only run the callback if the command and response ran successfully
    if command_task.exception() is None and response_task.exception() is None and result.status == status.SUCCESS:
        command.callback(response)
    else:
        print(f"Command !{command.name} with args {args} failed.")


def is_command(msg: str) -> bool:
    """
    Determines if a raw message body is a command
    :param msg: A raw message body
    :return: True if ``msg`` is a command, False otherwise.
    """
    # re.match looks for a match anywhere in msg. Regex matches if first
    # word of msg is ! followed by letters.
    return bool(re.match(r'^![a-zA-Z]+(\s|$)', msg))


def prepare_input(msg: str) -> str:
    """
    Reformats a message so that shlex is able to parse it properly.
    :param msg: The raw message input
    :return: The same message with any invalid characters removed or fixed.
    """
    # Convert curly quotes to straight quotes
    prepared = msg.replace('“', '"').replace('”', '"')
    return prepared
