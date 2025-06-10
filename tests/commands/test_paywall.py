from unittest import mock

import discord.ext.commands
import pytest

from memebot import commands
from memebot.lib import exception


class StringContaining(str):
    def __eq__(self, other):
        return self in other


class StringNotContaining(str):
    def __eq__(self, other):
        return self not in other


@pytest.mark.asyncio
async def test_paywall_command(mock_interaction: mock.Mock) -> None:
    link = "https://foo.com/poop"

    await commands.paywall.callback(mock_interaction, link)
    mock_interaction.response.send_message.assert_awaited_once_with(
        StringContaining(link)
    )


@pytest.mark.asyncio
async def test_paywall_command_strips_params(mock_interaction: mock.Mock) -> None:
    params = "?param1=foo&param2=bar"
    link = f"https://foo.com/poop{params}"

    await commands.paywall.callback(mock_interaction, link)
    mock_interaction.response.send_message.assert_awaited_once_with(
        StringNotContaining(params)
    )


@pytest.mark.asyncio
async def test_paywall_command_rejects_invalid_link(
    mock_interaction: mock.Mock,
) -> None:
    link = f"ftp://foo.com/poop"

    with pytest.raises(exception.MemebotUserError):
        await commands.paywall.callback(mock_interaction, link)
    mock_interaction.response.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_paywall_context_menu_succeeds_with_embed(
    mock_interaction: mock.Mock, mock_message: mock.Mock
) -> None:
    link = "https://foo.com/poop"
    bad_link = "http://bar.com/fart"
    mock_message.embeds = [mock.Mock(url=u) for u in (link, bad_link)]

    await commands.paywall_context_menu.callback(mock_interaction, mock_message)
    mock_interaction.response.send_message.assert_awaited_once_with(
        StringContaining(link)
    )


@pytest.mark.asyncio
async def test_paywall_context_menu_strips_params_from_embed(
    mock_interaction: mock.Mock, mock_message: mock.Mock
) -> None:
    params = "?param1=foo&param2=bar"
    link = f"https://foo.com/poop{params}"
    mock_message.embeds = [mock.Mock(url=link)]

    await commands.paywall_context_menu.callback(mock_interaction, mock_message)
    mock_interaction.response.send_message.assert_awaited_once_with(
        StringNotContaining(params)
    )


@pytest.mark.asyncio
async def test_paywall_context_menu_succeeds_with_content(
    mock_interaction: mock.Mock, mock_message: mock.Mock
) -> None:
    link = "https://foo.com/poop"
    bad_link = "http://bar.com/fart"
    mock_message.content = f"Hey gamers, check this out {link} {bad_link}"

    await commands.paywall_context_menu.callback(mock_interaction, mock_message)
    mock_interaction.response.send_message.assert_awaited_once_with(
        StringContaining(link)
    )


@pytest.mark.asyncio
async def test_paywall_context_menu_strips_params_from_content(
    mock_interaction: mock.Mock, mock_message: mock.Mock
) -> None:
    params = "?param1=foo&param2=bar"
    link = f"https://foo.com/poop{params}"
    mock_message.content = f"Hey gamers, check this out {link}"

    await commands.paywall_context_menu.callback(mock_interaction, mock_message)
    mock_interaction.response.send_message.assert_awaited_once_with(
        StringNotContaining(params)
    )


@pytest.mark.asyncio
async def test_paywall_context_menu_fails_with_no_link(
    mock_interaction: mock.Mock, mock_message: mock.Mock
) -> None:
    mock_message.content = ""
    with pytest.raises(exception.MemebotUserError):
        await commands.paywall_context_menu.callback(mock_interaction, mock_message)
    mock_interaction.response.send_message.assert_not_awaited()
