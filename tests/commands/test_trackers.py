from unittest import mock

import pytest

from memebot import commands
from memebot.lib import exception


class StringContaining(str):
    def __eq__(self, other):
        return self in other


@pytest.mark.asyncio
async def test_trackers_command(mock_interaction: mock.Mock) -> None:
    link = "https://example.com/page?utm_source=test"

    mock_interaction.response.defer = mock.AsyncMock()
    mock_interaction.followup.send = mock.AsyncMock()

    with mock.patch(
        "memebot.integrations.clear_urls.strip_trackers"
    ) as mock_strip_trackers:
        mock_strip_trackers.return_value = "https://example.com/page"
        await commands.trackers.callback(mock_interaction, link)

        mock_interaction.response.defer.assert_awaited_once_with(thinking=True)
        mock_interaction.followup.send.assert_awaited_once_with(
            StringContaining("https://example.com/page")
        )
        mock_strip_trackers.assert_called_once_with(link)


@pytest.mark.asyncio
async def test_trackers_command_rejects_invalid_link(
    mock_interaction: mock.Mock,
) -> None:
    link = "not-a-valid-url"

    mock_interaction.response.defer = mock.AsyncMock()
    mock_interaction.followup.send = mock.AsyncMock()

    with pytest.raises(exception.MemebotUserError):
        await commands.trackers.callback(mock_interaction, link)

    mock_interaction.response.defer.assert_not_called()
    mock_interaction.followup.send.assert_not_called()


@pytest.mark.asyncio
async def test_trackers_context_menu_with_link_in_content(
    mock_interaction: mock.Mock, mock_message: mock.Mock
) -> None:
    link = "https://example.com/page?utm_source=test"
    mock_message.content = f"Check out this link: {link}"

    mock_interaction.response.defer = mock.AsyncMock()
    mock_interaction.followup.send = mock.AsyncMock()

    with mock.patch("memebot.lib.util.extract_link") as mock_extract_link, mock.patch(
        "memebot.integrations.clear_urls.strip_trackers"
    ) as mock_strip_trackers:
        mock_extract_link.return_value = link
        mock_strip_trackers.return_value = "https://example.com/page"

        await commands.trackers_context_menu.callback(mock_interaction, mock_message)

        mock_extract_link.assert_called_once_with(mock_message)
        mock_strip_trackers.assert_called_once_with(link)
        mock_interaction.response.defer.assert_awaited_once_with(thinking=True)
        mock_interaction.followup.send.assert_awaited_once_with(
            StringContaining("https://example.com/page")
        )


@pytest.mark.asyncio
async def test_trackers_context_menu_with_link_in_embed(
    mock_interaction: mock.Mock, mock_message: mock.Mock
) -> None:
    link = "https://example.com/page?utm_source=test"
    mock_message.embeds = [mock.Mock(url=link)]
    mock_message.content = ""

    mock_interaction.response.defer = mock.AsyncMock()
    mock_interaction.followup.send = mock.AsyncMock()

    with mock.patch("memebot.lib.util.extract_link") as mock_extract_link, mock.patch(
        "memebot.integrations.clear_urls.strip_trackers"
    ) as mock_strip_trackers:
        mock_extract_link.return_value = link
        mock_strip_trackers.return_value = "https://example.com/page"

        await commands.trackers_context_menu.callback(mock_interaction, mock_message)

        mock_extract_link.assert_called_once_with(mock_message)
        mock_strip_trackers.assert_called_once_with(link)
        mock_interaction.response.defer.assert_awaited_once_with(thinking=True)
        mock_interaction.followup.send.assert_awaited_once_with(
            StringContaining("https://example.com/page")
        )


@pytest.mark.asyncio
async def test_trackers_context_menu_fails_with_no_link(
    mock_interaction: mock.Mock, mock_message: mock.Mock
) -> None:
    mock_message.content = "No link here"

    mock_interaction.response.defer = mock.AsyncMock()
    mock_interaction.followup.send = mock.AsyncMock()

    with mock.patch("memebot.lib.util.extract_link") as mock_extract_link:
        mock_extract_link.side_effect = exception.MemebotUserError("No link found")

        with pytest.raises(exception.MemebotUserError):
            await commands.trackers_context_menu.callback(
                mock_interaction, mock_message
            )

        mock_extract_link.assert_called_once_with(mock_message)
        mock_interaction.response.defer.assert_not_called()
        mock_interaction.followup.send.assert_not_called()
