import typing

import discord

from commands import Command, CommandOutput
from commands.command import has_subcommands
from lib import status
from .create import Create
from .delete import Delete
from .join import Join
from .leave import Leave
from .list import List


@has_subcommands(Create, Delete, Join, Leave, List)
class Role(Command):
    """
    Controls creating, joining, and leaving permissonless mentionable
    roles. These roles are intended to serve as "tags" to allow mentioning
    multiple users at once.

    !role create <role>: Creates <role>
    !role join <role>: Adds caller to <role>
    !role leave <role>: Removes caller from <role>
    !role delete <role>: Deletes <role> if <role> has no members
    !role list: List all bot-managed roles
    !role list <role>: Lists members of <role>

    Note that because role names are not unique, these commands will act
    on the first instance (hierarchically) of a role with name <role>
    """

    def __init__(self):
        super().__init__("role", "Self-contained role management")

    def help_text(self) -> CommandOutput:
        return CommandOutput().set_text(
            "Controls creating, joining, leaving, and listing permissionless mentionable roles. These roles are "
            "intended to serve as \"tags\" to allow mentioning multiple users at once."
        )

    async def exec(self, args: typing.List[str], message: discord.Message) -> CommandOutput:
        return self.fail(
            '\n'.join(f"`!{self.name} {sub.name} {sub.example_args}`: {sub.description}" for sub in Role.subcommands))


def action_failure_message(action: str, target_name: str, msg: str = "") -> CommandOutput:
    """
    Creates a failure message that explains which action failed and why
    :param action: The action which failed.
    :param target_name: The role upon which the action was to be performed.
    :param msg: The explanation, usually extracted from an exception.
    :return: A CommandOutput with the created message.
    """
    return CommandOutput(status=status.FAIL).set_text(f"Failed to {action} role {target_name}! {msg}")


def permission_failure_message(action: str, target_name: str) -> CommandOutput:
    """
    Creates a failure message that expresses failure due to lack of permissions.
    :param action: The action which failed.
    :param target_name: The role upon which the action was to be performed.
    :return: A CommandOutput with the created message.
    """
    # TODO: factor this out to be common to all commands
    return CommandOutput(status=status.FAIL).set_text(f"Memebot doesn't have permission to {action} role {target_name}. "
                                                       "Are you sure you configured Membot's permissions correctly?")


def find_role_by_name(target_name: str, guild: discord.Guild) -> discord.Role:
    """
    Finds a role by name.
    :param target_name: The name to search for.
    :param guild: The guild to search through.
    :return: A discord.Role object with the same name as ``target_name``.
    """
    for role in guild.roles:
        if role.name == target_name:
            return role


def get_reason(author_name: str) -> str:
    """
    Create a default reason string that will be embedded in new roles.
    :param author_name: The name of the user who initially created the role.
    :return: A string, displaying that a new role was created by ``author_name``
    """
    return f'Performed through MemeBot by {author_name}'
