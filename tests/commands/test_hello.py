from unittest import mock

import pytest

from memebot import commands


@pytest.mark.asyncio()
async def test_hello(mock_interaction: mock.Mock) -> None:
    await commands.hello.callback(mock_interaction)

    mock_interaction.response.send_message.assert_awaited_once_with(
        f"Hello, {mock_interaction.user.display_name}!"
    )