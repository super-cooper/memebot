import sys
from typing import List

from memebot import MemeBot


def main(argv: List[str]) -> int:
    """
    Main function, initializes MemeBot and then loops
    :param argv: Arguments
    :return: Exit status of discord.Client.run()
    """
    print(argv)
    client = MemeBot()

    # !! DO NOT HARDCODE THE TOKEN !!
    with open('client_token') as token_file:
        token = token_file.read().strip()

    return client.run(token)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
