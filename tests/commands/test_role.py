from typing import Optional, Type, Any
from unittest import mock

import discord.ext.commands
import pytest

from memebot import commands
from memebot.lib import exception

role_create: discord.ext.commands.Command
role_delete: discord.ext.commands.Command
role_join: discord.ext.commands.Command
role_leave: discord.ext.commands.Command
role_list: discord.ext.commands.Command


@pytest.fixture(autouse=True)
def resolve_role_functions() -> None:
    global role_create
    global role_delete
    global role_join
    global role_leave
    global role_list
    role_create = commands.role.get_command("create")
    role_delete = commands.role.get_command("delete")
    role_join = commands.role.get_command("join")
    role_leave = commands.role.get_command("leave")
    role_list = commands.role.get_command("list")


async def do_role_test(
    mock_interaction: mock.Mock,
    mock_guild: Optional[mock.Mock],
    command: discord.ext.commands.Command,
    *args: Any,
    **kwargs: Any,
) -> None:
    """
    Helper function for common role test pattern
    """
    mock_interaction.guild = mock_guild

    await command.callback(mock_interaction, *args, **kwargs)
    mock_interaction.response.send_message.assert_awaited_once()


async def do_role_test_failure(
    mock_interaction: mock.Mock,
    mock_guild: Optional[mock.Mock],
    exc_type: Type[Exception],
    command: discord.ext.commands.Command,
    *args: Any,
    **kwargs: Any,
) -> None:
    """
    Helper function for common role test pattern
    Only for test cases which throw
    """
    with pytest.raises(exc_type):
        await do_role_test(mock_interaction, mock_guild, command, *args, **kwargs)
    mock_interaction.response.send_message.assert_not_awaited()


async def do_role_create_failure(
    mock_interaction: mock.Mock,
    mock_guild: Optional[mock.Mock],
    role_name: str,
    exc_type: Type[Exception],
) -> None:
    """
    Helper function for common role_create failure test pattern
    """
    await do_role_test_failure(
        mock_interaction, mock_guild, exc_type, role_create, role_name
    )


async def do_role_create_success(
    mock_interaction: mock.Mock, mock_guild: Optional[mock.Mock], role_name: str
) -> None:
    """
    Helper function for common role_create test pattern
    """
    await do_role_test(mock_interaction, mock_guild, role_create, role_name)

    mock_interaction.guild.create_role.assert_awaited_once_with(
        name=role_name.lower(), mentionable=True, reason=mock.ANY
    )


@pytest.mark.parametrize("role_name", ["newrole", "nEWRole"])
@pytest.mark.asyncio
async def test_role_create_empty(
    mock_interaction: mock.Mock, mock_guild_empty: mock.Mock, role_name: str
) -> None:
    """
    Test basic successful creation of a new role
    """
    await do_role_create_success(mock_interaction, mock_guild_empty, role_name)


@pytest.mark.asyncio
async def test_role_create_populated(
    mock_interaction: mock.Mock, mock_guild_populated: mock.Mock
) -> None:
    """
    Tests successful creation of a new role when there exist other roles
    """
    await do_role_create_success(mock_interaction, mock_guild_populated, "anewrole")


@pytest.mark.parametrize("invalid_role_name", ["@newrole", "new@role"])
@pytest.mark.asyncio
async def test_role_create_invalid_name(
    mock_interaction: mock.Mock, mock_guild_empty: mock.Mock, invalid_role_name: str
) -> None:
    """
    Test failure to create a role with an invalid name
    """
    await do_role_create_failure(
        mock_interaction,
        mock_guild_empty,
        invalid_role_name,
        exception.MemebotUserError,
    )
    mock_guild_empty.create_role.assert_not_awaited()


@pytest.mark.asyncio
async def test_role_create_in_dm(mock_interaction: mock.Mock) -> None:
    """
    Test creating a role in DMs fails gracefully
    """
    await do_role_create_failure(
        mock_interaction, None, "dmrole", exception.MemebotUserError
    )


@pytest.mark.parametrize("conflict_name", ["conflictrole", "ConFlictROLE"])
@pytest.mark.asyncio
async def test_role_create_conflict(
    mock_interaction: mock.Mock, mock_guild_populated: mock.Mock, conflict_name: str
) -> None:
    """
    Test creating a role fails when there already exists a role with the same name
    """
    mock_guild_populated.roles[1].name = conflict_name.lower()
    await do_role_create_failure(
        mock_interaction,
        mock_guild_populated,
        conflict_name,
        exception.MemebotUserError,
    )
    mock_guild_populated.create_role.assert_not_called()


@pytest.mark.asyncio
async def test_role_create_permission_error(
    mock_interaction: mock.Mock,
    mock_guild_populated: mock.Mock,
) -> None:
    """
    Test attempting to create a role when Memebot doesn't have permission to do so
    """
    with mock.patch("requests.Response") as MockResponse:
        role_name = "forbiddenrole"
        # Force create_role to throw a dummy exception
        mock_guild_populated.create_role = mock.AsyncMock(
            side_effect=discord.Forbidden(MockResponse(), None)
        )
        await do_role_create_failure(
            mock_interaction,
            mock_guild_populated,
            role_name,
            exception.MemebotInternalError,
        )


@pytest.mark.asyncio
async def test_role_create_http_failure(
    mock_interaction: mock.Mock, mock_guild_populated: mock.Mock
) -> None:
    """
    Test role creation HTTP failures are handled gracefully
    """
    with mock.patch("requests.Response") as MockResponse:
        role_name = "failurerole"
        # Force create_role to throw a dummy exception
        mock_guild_populated.create_role = mock.AsyncMock(
            side_effect=discord.HTTPException(MockResponse(), None)
        )
        await do_role_create_failure(
            mock_interaction,
            mock_guild_populated,
            role_name,
            exception.MemebotInternalError,
        )


@pytest.mark.asyncio
async def test_role_delete_happy(
    mock_interaction: mock.Mock, mock_guild_populated: mock.Mock
) -> None:
    """
    Test deleting role from a guild which contains the role
    and the role only has 0 members
    """
    target_role = mock_guild_populated.roles[0]
    target_role.members = []
    await do_role_test(mock_interaction, mock_guild_populated, role_delete, target_role)

    # Check that delete was only called on the desired role
    for role in mock_guild_populated.roles:
        if role != target_role:
            role.delete.assert_not_awaited()
        else:
            role.delete.assert_awaited_once()


@pytest.mark.parametrize("n_members", [1, 10])
@pytest.mark.asyncio
async def test_role_delete_too_many_members(
    mock_interaction: mock.Mock, mock_guild_populated: mock.Mock, n_members: int
) -> None:
    """
    Test attempting to delete a role with any members fails gracefully
    """
    with mock.patch("discord.User") as MockUser:
        mock_users = [MockUser() for _ in range(n_members)]
        target_role = mock_guild_populated.roles[0]
        target_role.members = mock_users

        await do_role_test_failure(
            mock_interaction,
            mock_guild_populated,
            exception.MemebotUserError,
            role_delete,
            target_role,
        )

        target_role.delete.assert_not_awaited()


@pytest.mark.asyncio
async def test_role_delete_forbidden(
    mock_interaction: mock.Mock, mock_guild_populated: mock.Mock
) -> None:
    """
    Test attempting to delete a role when Memebot doesn't have permission to do so
    """
    with mock.patch("requests.Response") as MockResponse:
        target_role = mock_guild_populated.roles[2]
        # Force role.delete to throw a dummy exception
        target_role.delete = mock.AsyncMock(
            side_effect=discord.Forbidden(MockResponse(), None)
        )
        await do_role_test_failure(
            mock_interaction,
            mock_guild_populated,
            exception.MemebotInternalError,
            role_delete,
            target_role,
        )


@pytest.mark.asyncio
async def test_role_delete_http_failure(
    mock_interaction: mock.Mock, mock_guild_populated: mock.Mock
) -> None:
    """
    Test that HTTP failure during role deletion is handled gracefully
    """
    with mock.patch("requests.Response") as MockResponse:
        target_role = mock_guild_populated.roles[2]
        # Force role.delete to throw a dummy exception
        target_role.delete = mock.AsyncMock(
            side_effect=discord.HTTPException(MockResponse(), None)
        )
        await do_role_test_failure(
            mock_interaction,
            mock_guild_populated,
            exception.MemebotInternalError,
            role_delete,
            target_role,
        )


@pytest.mark.asyncio
async def test_role_join_happy(
    mock_interaction: mock.Mock, mock_guild_populated: mock.Mock
) -> None:
    """
    Tests successfully joining an existing role for a user with no roles
    """
    target_role = mock_guild_populated.roles[0]
    await do_role_test(mock_interaction, mock_guild_populated, role_join, target_role)
    mock_interaction.user.add_roles.assert_awaited_once_with(
        target_role, reason=mock.ANY
    )


@pytest.mark.asyncio
async def test_role_join_conflict(
    mock_interaction: mock.Mock, mock_guild_populated: mock.Mock
) -> None:
    """
    Test failure to join a role, because the caller is already in the role
    """
    target_role = mock_guild_populated.roles[0]
    mock_interaction.user.roles = [target_role]
    await do_role_test_failure(
        mock_interaction,
        mock_guild_populated,
        exception.MemebotUserError,
        role_join,
        target_role,
    )
    mock_interaction.user.add_roles.assert_not_awaited()
    mock_interaction.response.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_role_join_forbidden(
    mock_interaction: mock.Mock, mock_guild_populated: mock.Mock
) -> None:
    """
    Test that permission errors for role join are handled gracefully
    """
    with mock.patch("requests.Response") as MockResponse:
        target_role = mock_guild_populated.roles[2]
        # Force role.delete to throw a dummy exception
        mock_interaction.user.add_roles = mock.AsyncMock(
            side_effect=discord.Forbidden(MockResponse(), None)
        )
        await do_role_test_failure(
            mock_interaction,
            mock_guild_populated,
            exception.MemebotInternalError,
            role_join,
            target_role,
        )
    mock_interaction.user.add_roles.assert_awaited_once()


@pytest.mark.asyncio
async def test_role_join_failure(
    mock_interaction: mock.Mock, mock_guild_populated: mock.Mock
) -> None:
    """
    Test that permission errors for role join are handled gracefully
    """
    with mock.patch("requests.Response") as MockResponse:
        target_role = mock_guild_populated.roles[2]
        # Force role.delete to throw a dummy exception
        mock_interaction.user.add_roles = mock.AsyncMock(
            side_effect=discord.HTTPException(MockResponse(), None)
        )
        await do_role_test_failure(
            mock_interaction,
            mock_guild_populated,
            exception.MemebotInternalError,
            role_join,
            target_role,
        )
    mock_interaction.user.add_roles.assert_awaited_once()


@pytest.mark.asyncio
async def test_role_leave_with_membership(
    mock_interaction: mock.Mock, mock_guild_populated: mock.Mock
) -> None:
    """
    Test ability to leave a role the user is a member of
    """
    target_role = mock_guild_populated.roles[1]
    target_role.members = [mock_interaction.user]

    await do_role_test(mock_interaction, mock_guild_populated, role_leave, target_role)

    mock_interaction.user.remove_roles.assert_awaited_once_with(
        target_role, reason=mock.ANY
    )


@pytest.mark.asyncio
async def test_role_leave_no_membership(
    mock_interaction: mock.Mock, mock_guild_populated: mock.Mock
) -> None:
    """
    Test graceful failure for trying to leave a role the user is not a member of
    """
    target_role = mock_guild_populated.roles[1]
    target_role.members = []

    await do_role_test_failure(
        mock_interaction,
        mock_guild_populated,
        exception.MemebotUserError,
        role_leave,
        target_role,
    )
    mock_interaction.user.remove_roles.assert_not_awaited()


@pytest.mark.asyncio
async def test_role_leave_forbidden(
    mock_interaction: mock.Mock, mock_guild_populated: mock.Mock
) -> None:
    """
    Test graceful failure of calling role leave when memebot has bad permissions
    """
    with mock.patch("requests.Response") as MockResponse:
        target_role = mock_guild_populated.roles[2]
        target_role.members = [mock_interaction.user]
        # Force role.delete to throw a dummy exception
        mock_interaction.user.remove_roles = mock.AsyncMock(
            side_effect=discord.Forbidden(MockResponse(), None)
        )
        await do_role_test_failure(
            mock_interaction,
            mock_guild_populated,
            exception.MemebotInternalError,
            role_leave,
            target_role,
        )
    mock_interaction.user.remove_roles.assert_awaited_once()


@pytest.mark.asyncio
async def test_role_leave_failure(
    mock_interaction: mock.Mock, mock_guild_populated: mock.Mock
) -> None:
    """
    Test graceful failure of HTTP failure when calling role leave
    """
    with mock.patch("requests.Response") as MockResponse:
        target_role = mock_guild_populated.roles[2]
        target_role.members = [mock_interaction.user]
        # Force role.delete to throw a dummy exception
        mock_interaction.user.remove_roles = mock.AsyncMock(
            side_effect=discord.HTTPException(MockResponse(), None)
        )
        await do_role_test_failure(
            mock_interaction,
            mock_guild_populated,
            exception.MemebotInternalError,
            role_leave,
            target_role,
        )
    mock_interaction.user.remove_roles.assert_awaited_once()


@pytest.mark.asyncio
async def test_role_list_all_roles(
    mock_interaction: mock.Mock,
    mock_guild_populated: mock.Mock,
    mock_role_bot: mock.Mock,
    mock_role_everyone: mock.Mock,
) -> None:
    """
    Test ability to list all roles
    """
    await do_role_test(mock_interaction, mock_guild_populated, role_list, None)
    expected_output = f"Roles managed through `/role` command:\n- bar\n- baz\n- foo"
    mock_interaction.response.send_message.assert_awaited_once_with(expected_output)


@pytest.mark.asyncio
async def test_role_list_no_roles(
    mock_interaction: mock.Mock,
    mock_guild: mock.Mock,
    mock_role_bot: mock.Mock,
    mock_role_everyone: mock.Mock,
) -> None:
    """
    Test that role list works when there are no manageable roles
    """
    mock_guild.roles = discord.utils.SequenceProxy([mock_role_everyone, mock_role_bot])
    await do_role_test(mock_interaction, mock_guild, role_list, None)
    expected_output = f"Roles managed through `/role` command:"
    mock_interaction.response.send_message.assert_awaited_once_with(expected_output)


@pytest.mark.asyncio
async def test_role_list_user_own_roles(
    mock_interaction: mock.Mock,
    mock_guild_populated: mock.Mock,
    mock_role_bar: mock.Mock,
) -> None:
    """
    Test role list when retrieving roles of the user calling the command
    """
    target = mock_interaction.user
    mock_role_bar.members = discord.utils.SequenceProxy([target])
    await do_role_test(mock_interaction, mock_guild_populated, role_list, target)
    expected_output = (
        f"Roles for user {target.name} managed through `/role` command:\n- bar"
    )
    mock_interaction.response.send_message.assert_awaited_once_with(expected_output)


@pytest.mark.asyncio
async def test_role_list_other_user_roles(
    mock_interaction: mock.Mock,
    mock_guild_populated: mock.Mock,
    mock_role_bar: mock.Mock,
) -> None:
    """
    Test role list when retrieving roles of a user other than the one making the call
    """
    with mock.patch("discord.Member", spec=True) as MockMember:
        target = MockMember()
        mock_role_bar.members = discord.utils.SequenceProxy([target])
        await do_role_test(mock_interaction, mock_guild_populated, role_list, target)
        expected_output = (
            f"Roles for user {target.name} managed through `/role` command:\n- bar"
        )
        mock_interaction.response.send_message.assert_awaited_once_with(expected_output)


@pytest.mark.asyncio
async def test_role_list_user_no_roles(
    mock_interaction: mock.Mock, mock_guild_populated: mock.Mock
) -> None:
    """
    Test role list when retrieving roles of a user who is not in any manageable roles
    """
    target = mock_interaction.user
    await do_role_test(mock_interaction, mock_guild_populated, role_list, target)
    expected_output = f"Roles for user {target.name} managed through `/role` command:"
    mock_interaction.response.send_message.assert_awaited_once_with(expected_output)


@pytest.mark.asyncio
async def test_role_list_role(
    mock_interaction: mock.Mock,
    mock_guild_populated: mock.Mock,
    mock_role_bar: mock.Mock,
) -> None:
    """
    Test role list when retrieving members of a managed role
    """
    user = mock_interaction.user
    mock_role_bar.members = discord.utils.SequenceProxy([user])
    await do_role_test(mock_interaction, mock_guild_populated, role_list, mock_role_bar)
    expected = f"Members of `@{mock_role_bar.name}`:\n- {user.nick} ({user.name})"
    mock_interaction.response.send_message.assert_awaited_once_with(expected)


@pytest.mark.asyncio
async def test_role_list_role_no_members(
    mock_interaction: mock.Mock,
    mock_guild_populated: mock.Mock,
    mock_role_bar: mock.Mock,
) -> None:
    """
    Test role list when retrieving members of a role with no members
    """
    with pytest.raises(exception.MemebotUserError):
        await do_role_test(
            mock_interaction, mock_guild_populated, role_list, mock_role_bar
        )
    mock_interaction.response.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_role_list_role_not_managed(
    mock_interaction: mock.Mock, mock_guild_populated: mock.Mock
) -> None:
    """
    Test role list when retrieving members of a non-managed role
    """
    with mock.patch("discord.Role", spec=True) as MockRolePrivileged:
        mock_role_privileged = MockRolePrivileged()
        mock_role_privileged.members = discord.utils.SequenceProxy([])
        mock_guild_populated.roles = discord.utils.SequenceProxy(
            [
                # Append a role to the end of the list,
                # making it higher priority than the bot role
                *mock_guild_populated.roles,
                mock_role_privileged,
            ]
        )
    with pytest.raises(exception.MemebotUserError):
        # TODO I believe this only throws because the role is empty.
        #      Memebot *does* check non-managed roles via role list.
        #      Should it?
        await do_role_test(
            mock_interaction, mock_guild_populated, role_list, mock_role_privileged
        )
    mock_interaction.response.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_role_list_member(
    mock_interaction: mock.Mock,
    mock_guild_populated: mock.Mock,
    mock_member: mock.Mock,
    mock_role_bar: mock.Mock,
) -> None:
    """
    Test listing roles of a particular user
    """
    mock_role_bar.members = discord.utils.SequenceProxy([mock_member])
    await do_role_test(mock_interaction, mock_guild_populated, role_list, mock_member)
    mock_interaction.response.send_message.assert_awaited_once_with(
        f"Roles for user {mock_member.name} managed through `/role` command:"
        f"\n- {mock_role_bar.name}"
    )


@pytest.mark.asyncio
async def test_role_list_member_no_roles(
    mock_interaction: mock.Mock,
    mock_guild_populated: mock.Mock,
    mock_member: mock.Mock,
) -> None:
    """
    Test listing roles of a particular user which is not a member of any role
    """
    await do_role_test(mock_interaction, mock_guild_populated, role_list, mock_member)
    # TODO This does not respond with an error. Should it?
    #      Should the message be different if not?
    mock_interaction.response.send_message.assert_awaited_once_with(
        f"Roles for user {mock_member.name} managed through `/role` command:"
    )
