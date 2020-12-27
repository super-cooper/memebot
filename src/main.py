import sys

import config
from memebot import MemeBot


def main() -> int:
    """
    Main function, initializes MemeBot and then loops
    :return: Exit status of discord.Client.run()
    """
    client = MemeBot()

    # !! DO NOT HARDCODE THE TOKEN !!
    with open(config.discord_api_token) as token_file:
        token = token_file.read().strip()

    return client.run(token)


if __name__ == '__main__':
    sys.exit(main())
