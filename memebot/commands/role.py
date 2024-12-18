from typing import Optional, Any, Union

import discord

from memebot import log
from memebot.lib import exception


class RoleActionError(exception.MemebotUserError):
    def __init__(
        self, action: str, target_name: str, msg: str = "", *args: Any
    ) -> None:
        """
        Creates a failure message that explains which action failed and why
        :param action: The action which failed.
        :param target_name: The role upon which the action was to be performed.
        :param msg: The explanation, usually extracted from an exception.
        """
        super(RoleActionError, self).__init__(
            f"Failed to {action} role `@{target_name}`! {msg}", *args
        )


class RolePermissionError(exception.MemebotInternalError):
    def __init__(self, action: str, target_name: str, *args: Any) -> None:
        """
        Creates a failure message that expresses failure due to lack of permissions.
        TODO: factor this out to be common to all commands
        :param action: The action which failed.
        :param target_name: The role upon which the action was to be performed.
        :return: A CommandOutput with the created message.
        """
        super(RolePermissionError, self).__init__(
            f"Memebot doesn't have permission to {action} role `@{target_name}`. "
            "Are you sure you configured Memebot's permissions correctly?",
            *args,
        )


class RoleFailure(exception.MemebotInternalError):
    def __init__(self, action: str, target_name: str, *args: Any) -> None:
        """
        Unexpected, but handled internal failure
        """
        super(RoleFailure, self).__init__(
            f"Failed to {action} role `@{target_name}. "
            f"It seems that Discord's API is having problems.",
            *args,
        )


class RoleLocationError(exception.MemebotUserError):
    """
    Generic message for role commands which are executed in DMs
    """

    def __init__(self) -> None:
        super(RoleLocationError, self).__init__(
            "Unable to access roles outside of a server text channel."
        )


def get_reason(author_name: str) -> str:
    """
    Create a default reason string that will be embedded in new roles.
    :param author_name: The name of the user who initially created the role.
    :return: A string, displaying that a new role was created by ``author_name``
    """
    return f"Performed through MemeBot by {author_name}"


# Controls creating, joining, and leaving permissonless mentionable
# roles. These roles are intended to serve as "tags" to allow mentioning
# multiple users at once.
#
# /role create <role>: Creates <role>
# /role join <role>: Adds caller to <role>
# /role leave <role>: Removes caller from <role>
# /role delete <role>: Deletes <role> if <role> has no members
# /role list: List all bot-managed roles
# /role list <role>: Lists members of <role>
# /role list <user>: Lists roles of a user
#
# Note that because role names are not unique, these commands will act
# on the first instance (hierarchically) of a role with name <role>
role = discord.app_commands.Group(
    name="role",
    description="Controls creating, joining, and leaving roles.",
    guild_only=True,
)


@role.command()
async def create(interaction: discord.Interaction, role_name: str) -> None:
    """
    Create a new Memebot-managed role.
    """
    guild = interaction.guild
    author = interaction.user
    target_name = role_name.lower()
    if "@" in target_name:
        raise RoleActionError(
            "create",
            target_name,
            "Created roles cannot contain the `@` symbol.",
        )
    if not guild:
        raise RoleLocationError
    target_role = discord.utils.get(guild.roles, name=target_name)
    if target_role is not None:
        raise RoleActionError(
            "create", target_name, f"The role `@{target_name}` already exists!"
        )

    try:
        new_role = await guild.create_role(
            name=target_name, mentionable=True, reason=get_reason(author.name)
        )
        log.interaction(
            interaction, f"Created new role @{target_name} for {author.name}"
        )
    except discord.Forbidden:
        raise RolePermissionError("create", target_name)
    except discord.HTTPException:
        raise RoleFailure("create", target_name)

    await interaction.response.send_message(f"Created new role {new_role.mention}!")


@role.command()
async def delete(
    interaction: discord.Interaction,
    target_role: discord.Role,
) -> None:
    """
    Delete an empty Memebot-managed role.
    """
    # Ensure the role is empty before deleting
    if len(target_role.members) > 0:
        raise RoleActionError(
            "delete",
            target_role.name,
            "Roles must have no members to be deleted.",
        )

    try:
        await target_role.delete(reason=get_reason(interaction.user.name))
        log.interaction(
            interaction, f"Deleted role @{target_role.name} for {interaction.user.name}"
        )
    except discord.Forbidden:
        raise RolePermissionError("delete", target_role.name)
    except discord.HTTPException:
        raise RoleFailure("delete", target_role.name)

    await interaction.response.send_message(f"Deleted role `@{target_role.name}`")


@role.command()
async def join(
    interaction: discord.Interaction,
    target_role: discord.Role,
) -> None:
    """
    Join an existing Memebot-managed role
    """
    author = interaction.user
    if not isinstance(author, discord.Member):
        # Ensure the command was called from within a guild
        raise RoleLocationError
    if discord.utils.get(author.roles, name=target_role.name):
        raise RoleActionError(
            "join",
            target_role.name,
            f"{author.name} already a member of `@{target_role.name}`",
        )
    try:
        await author.add_roles(target_role, reason=get_reason(author.name))
        log.interaction(interaction, f"Added {author.name} to role @{target_role.name}")
    except discord.Forbidden:
        raise RolePermissionError("join", target_role.name)
    except discord.HTTPException:
        raise RoleFailure("join", target_role.name)

    await interaction.response.send_message(
        f"{author.name} successfully joined `@{target_role.name}`"
    )


@role.command()
async def leave(
    interaction: discord.Interaction,
    target_role: discord.Role,
) -> None:
    """
    Leave a Memebot-managed role.
    """
    author = interaction.user
    if author not in target_role.members:
        raise RoleActionError(
            "leave",
            target_role.name,
            f"User is not a member of `@{target_role.name}`.",
        )
    if not isinstance(author, discord.Member):
        # Ensure the command was called from within a server text channel
        raise RoleLocationError

    try:
        await author.remove_roles(target_role, reason=get_reason(author.name))
        log.interaction(
            interaction, f"Removed {author.name} from role @{target_role.name}"
        )
    except discord.Forbidden:
        raise RolePermissionError("leave", target_role.name)
    except discord.HTTPException:
        raise RoleFailure("leave", target_role.name)

    await interaction.response.send_message(
        f"{author.name} successfully left `@{target_role.name}`"
    )


@role.command(name="list")
async def role_list(
    interaction: discord.Interaction,
    target: Optional[Union[discord.Role, discord.Member]],
) -> None:
    """
    List all roles managed by Memebot, all managed roles of which a user is a member,
    or all members of a role managed by Memebot.
    """
    if not interaction.guild:
        raise RoleLocationError

    if isinstance(target, discord.Role):
        if not target.members:
            raise RoleActionError(
                "list",
                target.name,
                msg=f"Role `@{target.name}` has no members!",
            )

        member_names = [
            f"{member.nick} ({member.name})" if member.nick else member.name
            for member in target.members
        ]

        member_names.sort()
        member_names.insert(0, f"Members of `@{target.name}`:")

        log.interaction(
            interaction,
            f"Listed members of @{target.name} for {interaction.user.name}",
        )
        await interaction.response.send_message(
            content="\n- ".join(member_names), ephemeral=True
        )
    else:
        bot_user = interaction.client.user
        if not bot_user:
            raise exception.MemebotInternalError("Cannot get bot user from interaction")
        roles = []
        can_manage = False
        # Memebot can manage all roles below its highest role.
        # Find that role and begin listing roles from that point onward.
        # TODO in the future, we can just store the managed roles in the database
        for role_obj in interaction.guild.roles[:0:-1]:  # Top-down, excluding @everyone
            if can_manage and role_obj.name != bot_user.name:
                if target is None or target in role_obj.members:
                    roles.append(role_obj.name)
            elif bot_user in role_obj.members:
                can_manage = True
        roles.sort()

        usr_msg = f"for user {target.name} " if target else ""
        roles.insert(
            0,
            f"Roles {usr_msg}managed through `/role` command:",
        )
        log.interaction(interaction, f"Listed roles for {interaction.user.name}")
        await interaction.response.send_message(
            content="\n- ".join(roles), ephemeral=True
        )
