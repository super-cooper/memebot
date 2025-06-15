import logging
import os
import sys
from datetime import timedelta
from unittest import mock

import pytest

from memebot import config
from memebot import log

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

    config.log_level = logging.DEBUG
    config.log_location = logging.StreamHandler(sys.stdout)
    log.configure_logging()

    # Ensure rules are not refreshed automatically
    config.clearurls_rules_refresh_hours = timedelta(days=365 * 1000)

    # Run test
    yield

    # Tear down
