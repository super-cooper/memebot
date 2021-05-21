# Memebot 

This is MemeBot, a discord bot.

If you are hosting yourself, you will need to create a file in the root directory of your local repository called 
`client_token` and paste your Discord developer client token into that file. Nothing else should be in the file.
Usage of the bot is as follows:

```
usage: main.py [-h] [--discord-api-token DISCORD_API_TOKEN] [--twitter-api-tokens TWITTER_API_TOKENS] [--log-level LOG_LEVEL] [--log-location LOG_LOCATION] [--no-twitter] [--nodb] [--database-uri DATABASE_URI]

optional arguments:
  -h, --help            show this help message and exit
  --discord-api-token DISCORD_API_TOKEN
                        Path to the file containing the Discord API token
  --twitter-api-tokens TWITTER_API_TOKENS
                        Path to the file containing the Twitter API tokens, in JSON format.
  --log-level LOG_LEVEL
                        Set the log level for MemeBot.
  --log-location LOG_LOCATION
                        Set the location for MemeBot's log (stdout, stderr, syslog, /path/to/file)
  --no-twitter          Disable Twitter integration
  --nodb                Disable the database connection, and all features which require it.
  --database-uri DATABASE_URI
                        URI of the MongoDB database server
```

Current commands that can be used in Discord:

    !hello - Say "hello" to Memebot!
    !help  - Learn how to use MemeBot
    !poll  - Create a simple poll.
    !role  - Self-contained role management

## Docker
Memebot has a straightforward Docker image that can be build based on the [Dockerfile](./docker/Dockerfile) in this 
repository. This image can be used for both deployment and testing purposes.
