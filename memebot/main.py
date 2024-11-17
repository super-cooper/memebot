from memebot import config
from memebot import log
from memebot.client import get_memebot


def main() -> None:
    """
    Main function, initializes MemeBot and then loops
    :return: Exit status of discord.Client.run()
    """
    config.populate_config_from_command_line()
    # the ``log`` package should be imported ASAP to ensure our logging shims
    # are injected into the runtime before external packages configure
    # their logging
    log.info("Starting up memebot!")
    memebot = get_memebot()

    # !! DO NOT HARDCODE THE TOKEN !!
    memebot.run(config.discord_api_token)


if __name__ == "__main__":
    main()
