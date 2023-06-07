import argparse
import logging
import os
import urllib.parse

from memebot.config import validators

# Discord API token
discord_api_token: str
# Twitter API tokens
twitter_api_bearer_token: str

# The logging level for MemeBot
log_level: str
# The location for MemeBot's log
log_location: logging.Handler

# Flag which tells if Twitter integration is enabled
twitter_enabled: bool

# Flag which tells if a database connection is enabled
database_enabled: bool
# MongoDB URI
database_uri: urllib.parse.ParseResult


def populate_config_from_command_line() -> None:
    parser = argparse.ArgumentParser()

    # API Tokens
    parser.add_argument(
        "--discord-api-token",
        help="The Discord API client token",
        default=os.getenv("MEMEBOT_DISCORD_CLIENT_TOKEN"),
        type=str,
    )
    parser.add_argument(
        "--twitter-api-consumer-key",
        help="(DEPRECATED) The Twitter API consumer key",
        default=os.getenv("MEMEBOT_TWITTER_CONSUMER_KEY"),
        type=lambda _: print(
            "USING DEPRECATED TWITTER OAUTH 1.0 CREDENTIALS! "
            "PLEASE USE BEARER TOKENS INSTEAD!"
        ),
    )
    parser.add_argument(
        "--twitter-api-consumer-secret",
        help="(DEPRECATED) The Twitter API consumer secret",
        default=os.getenv("MEMEBOT_TWITTER_CONSUMER_SECRET"),
        type=lambda _: print(
            "USING DEPRECATED TWITTER OAUTH 1.0 CREDENTIALS! "
            "PLEASE USE BEARER TOKENS INSTEAD!"
        ),
    )
    parser.add_argument(
        "--twitter-api-bearer-token",
        help="The Twitter API OAuth 2.0 bearer token",
        default=os.getenv("MEMEBOT_TWITTER_BEARER_TOKEN"),
        type=str,
    )

    # Logging Configuration
    logging_verbosity_group = parser.add_mutually_exclusive_group()
    # Accept all log levels recognized by the logging library except NOTSET
    logging_verbosity_group.add_argument(
        "--log-level",
        help="Set logging level",
        choices=[
            logging.getLevelName(level)
            for level in (
                logging.DEBUG,
                logging.INFO,
                logging.WARN,
                logging.ERROR,
                logging.CRITICAL,
            )
        ],
        default=os.getenv("MEMEBOT_LOG_LEVEL", logging.getLevelName(logging.INFO)),
        type=str,
    )
    logging_verbosity_group.add_argument(
        "-v",
        "--verbose",
        help="Use verbose logging. Equivalent to --log-level DEBUG",
        dest="log_level",
        action="store_const",
        const=logging.getLevelName(logging.DEBUG),
    )
    parser.add_argument(
        "--log-location",
        help="Set the location for MemeBot's log",
        default=os.getenv("MEMEBOT_LOG_LOCATION", "stdout"),
        metavar="{stdout,stderr,syslog,/path/to/file}",
        type=validators.validate_log_location,
    )

    # Twitter Integration
    parser.add_argument(
        "--no-twitter",
        help="Disable Twitter integration",
        dest="twitter_enabled",
        action="store_false",
    )
    parser.set_defaults(
        twitter_enabled=validators.validate_bool(
            os.getenv("MEMEBOT_TWITTER_ENABLED", str(True))
        )
    )

    # Database Configuration
    parser.add_argument(
        "--nodb",
        help="Disable the database connection, and all features which require it.",
        dest="database_enabled",
        action="store_false",
    )
    parser.set_defaults(
        database_enabled=validators.validate_bool(
            os.getenv("MEMEBOT_DATABASE_ENABLED", str(True))
        )
    )

    parser.add_argument(
        "--database-uri",
        help="URI of the MongoDB database server",
        default=urllib.parse.urlparse(
            os.getenv("MEMEBOT_DATABASE_URI", "mongodb://127.0.0.1:27017")
        ),
        type=urllib.parse.urlparse,
    )

    args = parser.parse_args()

    global discord_api_token
    global twitter_api_bearer_token
    discord_api_token = args.discord_api_token
    twitter_api_bearer_token = args.twitter_api_bearer_token

    global log_level
    global log_location
    log_level = args.log_level
    log_location = args.log_location

    global twitter_enabled
    twitter_enabled = args.twitter_enabled

    global database_enabled
    global database_uri
    database_enabled = args.database_enabled
    database_uri = args.database_uri
