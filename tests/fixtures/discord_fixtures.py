from unittest import mock

import discord.utils
import pytest


@pytest.fixture
@mock.patch("discord.Client", spec=True)
def mock_discord_client(mock_client: type[mock.Mock]) -> mock.Mock:
    return mock_client()


@pytest.fixture
@mock.patch("discord.Interaction", spec=True)
def mock_interaction(
    mock_interaction: type[mock.Mock], mock_message: mock.Mock, mock_member: mock.Mock
) -> mock.Mock:
    """
    Generates a mock interaction with basic behavior.
    """
    interaction = mock_interaction()

    interaction.response.send_message = mock.AsyncMock()
    interaction.original_response = mock.AsyncMock(return_value=mock_message)
    interaction.user = mock_member

    return interaction


@pytest.fixture
@mock.patch("discord.Message", spec=True)
def mock_message(mock_message: type[mock.Mock]) -> mock.Mock:
    """
    Generates a mock message with basic behavior.
    """
    message = mock_message()

    message.add_reaction = mock.AsyncMock()
    message.channel.send = mock.AsyncMock()

    return message


@pytest.fixture
@mock.patch("discord.Member", spec=True)
def mock_member(mock_member: type[mock.Mock]) -> mock.Mock:
    member = mock_member()
    member.roles = []
    member.add_roles = mock.AsyncMock()
    return member


@pytest.fixture
@mock.patch("discord.Guild", spec=True)
def mock_guild(mock_guild: type[mock.Mock]) -> mock.Mock:
    """
    Creates a default mock Guild
    """
    guild = mock_guild()

    guild.create_role = mock.AsyncMock()

    return guild


@pytest.fixture
def mock_guild_empty(mock_guild: mock.Mock) -> mock.Mock:
    """
    Generates a guild with empty iterables
    """
    mock_guild.roles = discord.utils.SequenceProxy([])

    return mock_guild


def mock_role_with_attrs(
    role_type: type[mock.Mock], name: str | None = None
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
def mock_role_everyone(
    mock_role_everyone: type[mock.Mock], mock_interaction: mock.Mock
) -> mock.Mock:
    everyone = mock_role_with_attrs(mock_role_everyone, "everyone")
    everyone.members = discord.utils.SequenceProxy([mock_interaction.client.user])
    return everyone


@pytest.fixture
@mock.patch("discord.Role", spec=True)
def mock_role_bot(
    mock_role_bot: type[mock.Mock], mock_interaction: mock.Mock
) -> mock.Mock:
    bot_role = mock_role_with_attrs(mock_role_bot, "bot")
    bot_role.members = discord.utils.SequenceProxy([mock_interaction.client.user])
    return bot_role


@pytest.fixture
@mock.patch("discord.Role", spec=True)
def mock_role_foo(mock_role_foo: type[mock.Mock]) -> list[mock.Mock]:
    return mock_role_with_attrs(mock_role_foo, "foo")


@pytest.fixture
@mock.patch("discord.Role", spec=True)
def mock_role_bar(mock_role_bar: type[mock.Mock]) -> list[mock.Mock]:
    return mock_role_with_attrs(mock_role_bar, "bar")


@pytest.fixture
@mock.patch("discord.Role", spec=True)
def mock_role_baz(mock_role_baz: type[mock.Mock]) -> list[mock.Mock]:
    return mock_role_with_attrs(mock_role_baz, "baz")


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
