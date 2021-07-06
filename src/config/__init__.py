import argparse
import logging
import pathlib
import urllib.parse

from config import validators

# Path to the file containing the Discord API token
discord_api_token: pathlib.Path
# Path to the JSON file containing the Twitter API tokens
twitter_api_tokens: pathlib.Path

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

    # Logging Configuration
    logging_verbosity_group = parser.add_mutually_exclusive_group()
    # Accept all log levels recognized by the logging library except NOTSET
    logging_verbosity_group.add_argument("--log-level",
                                         help=f"Set logging level",
                                         choices=[logging.getLevelName(level) for level in (
                                             logging.DEBUG, logging.INFO, logging.WARN, logging.ERROR,
                                             logging.CRITICAL)],
                                         default=logging.getLevelName(logging.INFO),
                                         type=str)
    logging_verbosity_group.add_argument("-v",
                                         "--verbose",
                                         help="Use verbose logging. Equivalent to --log-level DEBUG",
                                         dest="log_level",
                                         action="store_const",
                                         const=logging.getLevelName(logging.DEBUG))
    parser.add_argument("--log-location",
                        help="Set the location for MemeBot's log",
                        default="stdout",
                        metavar="{stdout,stderr,syslog,/path/to/file}",
                        type=validators.validate_log_location)

    # Twitter Integration
    parser.add_argument("--no-twitter",
                        help="Disable Twitter integration",
                        dest="twitter_enabled",
                        action="store_false")
    parser.set_defaults(twitter_enabled=True)

    # Database Configuration
    parser.add_argument("--nodb",
                        help="Disable the database connection, and all features which require it.",
                        dest="database_enabled",
                        action="store_false")
    parser.set_defaults(database_enabled=True)

    parser.add_argument("--database-uri",
                        help="URI of the MongoDB database server",
                        default=urllib.parse.urlparse("mongodb://127.0.0.1:27017"),
                        type=urllib.parse.urlparse)

    args = parser.parse_args()

    global discord_api_token
    global twitter_api_tokens
    discord_api_token = args.discord_api_token
    twitter_api_tokens = args.twitter_api_tokens

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


populate_config_from_command_line()
