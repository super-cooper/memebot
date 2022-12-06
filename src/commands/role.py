from typing import Optional, Any, Union, Annotated

import discord
import discord.ext.commands

from lib import exception


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


class RoleLocationError(exception.MemebotUserError):
    """
    Generic message for role commands which are executed in DMs
    """

    def __init__(self) -> None:
        super(RoleLocationError, self).__init__(
            "Unable to access roles outside of a server text channel."
        )


class LowercaseRoleConverter(discord.ext.commands.RoleConverter):
    """
    Argument converter for converting a command argument to a discord.Role object
    whose name matches the lowercased argument.
    """

    async def convert(
        self, ctx: discord.ext.commands.Context, arg: str
    ) -> discord.Role:
        return await super().convert(ctx, arg.lower())


def get_reason(author_name: str) -> str:
    """
    Create a default reason string that will be embedded in new roles.
    :param author_name: The name of the user who initially created the role.
    :return: A string, displaying that a new role was created by ``author_name``
    """
    return f"Performed through MemeBot by {author_name}"


@discord.ext.commands.group(
    brief="Self-contained role management",
    help="Controls creating, joining, leaving, and listing permissionless mentionable roles. "
    'These roles are intended to serve as "tags" to allow mentioning multiple users at once.',
)
async def role(ctx: discord.ext.commands.Context) -> None:
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
    !role list <user>: Lists roles of a user

    Note that because role names are not unique, these commands will act
    on the first instance (hierarchically) of a role with name <role>
    """
    if not ctx.invoked_subcommand:
        raise exception.MemebotUserError


@role.command(  # type: ignore
    brief="Creates <role>", help="Create a new role to be managed by Memebot."
)
async def create(ctx: discord.ext.commands.Context, role_name: str) -> None:
    """
    Create a new memebot-managed role.
    """
    guild = ctx.guild
    author = ctx.author
    target_name = role_name.lower()
    if not ctx.command:
        raise exception.MemebotInternalError("Cannot get command from context")
    if "@" in target_name:
        raise RoleActionError(
            ctx.command.name,
            target_name,
            "Created roles cannot contain the `@` symbol.",
        )
    if not guild:
        raise RoleLocationError
    target_role = discord.utils.get(guild.roles, name=target_name)
    if target_role is not None:
        raise RoleActionError(
            ctx.command.name, target_name, f"The role `@{target_name}` already exists!"
        )

    try:
        new_role = await guild.create_role(
            name=target_name, mentionable=True, reason=get_reason(author.name)
        )
    except discord.Forbidden:
        raise RolePermissionError(ctx.command.name, target_name)
    except (discord.HTTPException, TypeError):
        raise RoleActionError(ctx.command.name, target_name)

    await ctx.send(f"Created new role {new_role.mention}!")


@role.command(  # type: ignore
    brief="Deletes <role> if <role> has no members.",
    help="Delete a Memebot-managed role if, and only if, the role has no members.",
)
async def delete(
    ctx: discord.ext.commands.Context,
    target_role: Annotated[discord.Role, LowercaseRoleConverter],
) -> None:
    if not ctx.command:
        raise exception.MemebotInternalError("Cannot get command from context")

    # Ensure the role is empty before deleting
    if len(target_role.members) > 0:
        raise RoleActionError(
            ctx.command.name,
            target_role.name,
            "Roles must have no members to be deleted.",
        )

    try:
        await target_role.delete(reason=get_reason(ctx.author.name))
    except discord.Forbidden:
        raise RolePermissionError(ctx.command.name, target_role.name)
    except discord.HTTPException:
        raise RoleActionError(ctx.command.name, target_role.name)

    await ctx.send(f"Deleted role `@{target_role.name}`")


@role.command(  # type: ignore
    brief="Adds caller to <role>", help="Join an existing Memebot-managed role."
)
async def join(
    ctx: discord.ext.commands.Context,
    target_role: Annotated[discord.Role, LowercaseRoleConverter],
) -> None:
    """
    Join an existing Memebot-managed role
    """
    if not ctx.command:
        raise exception.MemebotInternalError("Cannot get command from context")

    author = ctx.author
    if not isinstance(author, discord.Member):
        # Ensure the command was called from within a server text channel
        raise RoleLocationError
    if discord.utils.get(author.roles, name=target_role.name):
        raise RoleActionError(
            ctx.command.name,
            target_role.name,
            f"{author.name} already a member of `@{target_role.name}`",
        )
    try:
        await author.add_roles(target_role, reason=get_reason(author.name))
    except discord.Forbidden:
        raise RolePermissionError(ctx.command.name, target_role.name)
    except discord.HTTPException:
        raise RoleActionError(ctx.command.name, target_role.name)

    await ctx.send(f"{author.name} successfully joined `@{target_role.name}`")


@role.command(  # type: ignore
    brief="Removes caller from <role>",
    help="Leave a Memebot-managed role.",
)
async def leave(
    ctx: discord.ext.commands.Context,
    target_role: Annotated[discord.Role, LowercaseRoleConverter],
) -> None:
    """
    Leave a Memebot-managed role of which the caller is a member
    """
    if not ctx.command:
        raise exception.MemebotInternalError("Cannot get command from context")

    author = ctx.author
    if author not in target_role.members:
        raise RoleActionError(
            ctx.command.name,
            target_role.name,
            f"User is not a member of `@{target_role.name}`.",
        )
    if not isinstance(author, discord.Member):
        # Ensure the command was called from within a server text channel
        raise RoleLocationError

    try:
        await author.remove_roles(target_role, reason=get_reason(author.name))
    except discord.Forbidden:
        raise RolePermissionError(ctx.command.name, target_role.name)
    except discord.HTTPException:
        raise RoleActionError(ctx.command.name, target_role.name)

    await ctx.send(f"{author.name} successfully left `@{target_role.name}`")


@role.command(  # type: ignore
    name="list",
    brief="List all roles managed by Memebot, all members of a given role, or all roles of a given user.",
    help="List all roles managed by Memebot. Optionally, if the name of a role is provided, list "
    "all members of that role, or if a username is provided, list all roles for that user.",
)
async def role_list(
    ctx: discord.ext.commands.Context,
    target: Optional[
        Union[Annotated[discord.Role, LowercaseRoleConverter], discord.Member]
    ],
) -> None:
    """
    List all roles managed by Memebot, or all members of a role managed by Memebot.
    """
    if not ctx.command:
        raise exception.MemebotInternalError("Cannot get command from context")

    if not ctx.guild:
        raise RoleLocationError

    if isinstance(target, discord.Role):
        if not target.members:
            raise RoleActionError(
                ctx.command.name,
                target.name,
                msg=f"Role `@{target.name}` has no members!",
            )

        member_names = [
            f"{member.nick} ({member.name})" if member.nick else member.name
            for member in target.members
        ]

        member_names.sort()
        member_names.insert(0, f"Members of `@{target.name}`:")

        await ctx.send("\n- ".join(member_names))
    else:
        roles = []
        can_manage = False
        # Memebot can manage all roles below its highest role.
        # Find that role and begin listing roles from that point onward.
        # TODO in the future, we can just store the managed roles in the database
        for role_obj in ctx.guild.roles[:0:-1]:  # Top-down, excluding @everyone
            if can_manage and role_obj.name != ctx.bot.user.name:
                if target is None or target in role_obj.members:
                    roles.append(role_obj.name)
            elif ctx.bot.user in role_obj.members:
                can_manage = True
        roles.sort()

        usr_msg = f"for user {target.name} " if target else ""
        roles.insert(
            0,
            f"Roles {usr_msg}managed through `{ctx.prefix}{ctx.command.parent}` command:",
        )
        await ctx.send("\n- ".join(roles))
