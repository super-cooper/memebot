# In order to ensure consistent logging,
# log must always be the first thing imported by the main module
import log

import config
import memebot


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
