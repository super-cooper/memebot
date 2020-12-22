import sys

from memebot import MemeBot


def main() -> int:
    """
    Main function, initializes MemeBot and then loops
    :return: Exit status of discord.Client.run()
    """
    client = MemeBot()

    # !! DO NOT HARDCODE THE TOKEN !!
    with open('client_token') as token_file:
        token = token_file.read().strip()

    with open('twitter_api_tokens.json') as twitter_api_tokens:
        twitter_tokens = json.load(twitter_api_tokens)

    return client.run(token)

if __name__ == '__main__':
    sys.exit(main())
