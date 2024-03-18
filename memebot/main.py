from memebot import config

config.populate_config_from_command_line()

from memebot.client import memebot
from memebot import log


def main() -> None:
    """
    Main function, initializes MemeBot and then loops
    :return: Exit status of discord.Client.run()
    """
    log.set_third_party_logging()

    # !! DO NOT HARDCODE THE TOKEN !!
    memebot.run(config.discord_api_token)


if __name__ == "__main__":
    main()
