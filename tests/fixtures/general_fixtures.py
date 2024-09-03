import os
from unittest import mock

import pytest

from memebot import config
from memebot.integrations import twitter

DEFAULT_ENVIRONMENT = os.environ | {
    "MEMEBOT_DISCORD_CLIENT_TOKEN": "MOCK_TOKEN",
    "MEMEBOT_TWITTER_ENABLED": "False",
}


@pytest.fixture(autouse=True)
def setup_and_teardown(mock_twitter_client: mock.Mock) -> None:
    """
    This is a universal setup and teardown function which is automatically run
    surrounding each test. The function contains both the setup and teardown behavior.
    The ``yield`` statement is where the test is run.
    """
    # Set up
    # This creates a simple base environment. Tests that require specific configuration
    # can overwrite the variables they need
    os.environ = DEFAULT_ENVIRONMENT

    with mock.patch("argparse.ArgumentParser", mock.MagicMock()):
        with mock.patch("tweepy.Client", lambda *_, **__: mock_twitter_client):
            config.populate_config_from_command_line()
            twitter.init(mock.MagicMock())

    # Run test
    yield

    # Tear down
