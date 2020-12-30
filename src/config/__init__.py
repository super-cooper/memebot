import argparse
import pathlib

discord_api_token: pathlib.Path
twitter_api_tokens: pathlib.Path


def populate_config_from_command_line():
    parser = argparse.ArgumentParser()

    # API Tokens
    parser.add_argument("--discord-api-token",
                        help="Path to the file containing the Discord API token",
                        default="client_token",
                        type=pathlib.Path)
    parser.add_argument("--twitter-api-tokens",
                        help="Path to the file containing the Twitter API tokens, in JSON format.",
                        default="twitter_api_tokens.json",
                        type=pathlib.Path)

    args = parser.parse_args()

    global discord_api_token
    global twitter_api_tokens
    discord_api_token = args.discord_api_token
    twitter_api_tokens = args.twitter_api_tokens


populate_config_from_command_line()
