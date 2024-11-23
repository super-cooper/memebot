import os
from unittest import mock

import pytest

from memebot import config

DEFAULT_ENVIRONMENT = os.environ | {
    "MEMEBOT_DISCORD_CLIENT_TOKEN": "MOCK_TOKEN",
}


@pytest.fixture(autouse=True)
def setup_and_teardown() -> None:
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
        config.populate_config_from_command_line()

    # Run test
    yield

    # Tear down
