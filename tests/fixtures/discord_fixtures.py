from typing import Type, Optional
from unittest import mock

import discord.utils
import pytest


@pytest.fixture
@mock.patch("discord.Client", spec=True)
def mock_discord_client(MockClient: type[mock.Mock]) -> mock.Mock:
    return MockClient()

@pytest.fixture
@mock.patch("discord.Interaction", spec=True)
def mock_interaction(
    MockInteraction: Type[mock.Mock], mock_message: mock.Mock, mock_member: mock.Mock
) -> mock.Mock:
    """
    Generates a mock interaction with basic behavior.
    """
    mock_interaction = MockInteraction()

    mock_interaction.response.send_message = mock.AsyncMock()
    mock_interaction.original_response = mock.AsyncMock(return_value=mock_message)
    mock_interaction.user = mock_member

    return mock_interaction


@pytest.fixture
@mock.patch("discord.Message", spec=True)
def mock_message(MockMessage: Type[mock.Mock]) -> mock.Mock:
    """
    Generates a mock message with basic behavior.
    """
    mock_message = MockMessage()

    mock_message.add_reaction = mock.AsyncMock()
    mock_message.channel.send = mock.AsyncMock()

    return mock_message


@pytest.fixture
@mock.patch("discord.Member", spec=True)
def mock_member(MockMember: Type[mock.Mock]) -> mock.Mock:
    mock_member = MockMember()
    mock_member.roles = []
    mock_member.add_roles = mock.AsyncMock()
    return mock_member


@pytest.fixture
@mock.patch("discord.Guild", spec=True)
def mock_guild(MockGuild: Type[mock.Mock]) -> mock.Mock:
    """
    Creates a default mock Guild
    """
    mock_guild = MockGuild()

    mock_guild.create_role = mock.AsyncMock()

    return mock_guild


@pytest.fixture
def mock_guild_empty(mock_guild: mock.Mock) -> mock.Mock:
    """
    Generates a guild with empty iterables
    """
    mock_guild.roles = discord.utils.SequenceProxy([])

    return mock_guild


def mock_role_with_attrs(
    role_type: Type[mock.Mock], name: Optional[str] = None
) -> mock.Mock:
    """
    Generates a unique mock role with specified attributes
    """
    role = role_type(name=name)
    role.delete = mock.AsyncMock()
    role.members = discord.utils.SequenceProxy([])
    if name is not None:
        role.name = name
    return role


@pytest.fixture
@mock.patch("discord.Role", spec=True)
def mock_role_everyone(MockRoleEveryone: Type[mock.Mock], mock_interaction: mock.Mock) -> mock.Mock:
    everyone = mock_role_with_attrs(MockRoleEveryone, "everyone")
    everyone.members = discord.utils.SequenceProxy([mock_interaction.client.user])
    return everyone


@pytest.fixture
@mock.patch("discord.Role", spec=True)
def mock_role_bot(MockRoleBot: Type[mock.Mock], mock_interaction: mock.Mock) -> mock.Mock:
    bot_role = mock_role_with_attrs(MockRoleBot, "bot")
    bot_role.members = discord.utils.SequenceProxy([mock_interaction.client.user])
    return bot_role


@pytest.fixture
@mock.patch("discord.Role", spec=True)
def mock_role_foo(MockRoleFoo: Type[mock.Mock]) -> list[mock.Mock]:
    return mock_role_with_attrs(MockRoleFoo, "foo")


@pytest.fixture
@mock.patch("discord.Role", spec=True)
def mock_role_bar(MockRoleBar: Type[mock.Mock]) -> list[mock.Mock]:
    return mock_role_with_attrs(MockRoleBar, "bar")


@pytest.fixture
@mock.patch("discord.Role", spec=True)
def mock_role_baz(MockRoleBaz: Type[mock.Mock]) -> list[mock.Mock]:
    return mock_role_with_attrs(MockRoleBaz, "baz")


@pytest.fixture
def mock_guild_populated(
    mock_guild: mock.Mock,
    mock_role_everyone: mock.Mock,
    mock_role_bot: mock.Mock,
    mock_role_foo: mock.Mock,
    mock_role_bar: mock.Mock,
    mock_role_baz: mock.Mock,
) -> mock.Mock:
    mock_guild.roles = discord.utils.SequenceProxy(
        # Roles ordered in reverse priority
        [mock_role_everyone, mock_role_baz, mock_role_bar, mock_role_foo, mock_role_bot]
    )
    return mock_guild
