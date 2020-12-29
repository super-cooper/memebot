# Memebot 

This is MemeBot, a discord bot.

If you are hosting yourself, you will need to create a file in the root directory of your local repository called 
`client_token` and paste your Discord developer client token into that file. Nothing else should be in the file.
Usage of the bot is as follows:

```
usage: main.py [-h] [--discord-api-token DISCORD_API_TOKEN] [--twitter-api-tokens TWITTER_API_TOKENS]

optional arguments:
  -h, --help            show this help message and exit
  --discord-api-token DISCORD_API_TOKEN
                        Path to the file containing the Discord API token
  --twitter-api-tokens TWITTER_API_TOKENS
                        Path to the file containing the Twitter API tokens, in JSON format.
```

Current commands that can be used in Discord:

    !hello - Say "hello" to Memebot!
    !help  - Learn how to use MemeBot
    !poll  - Create a simple poll.
    !role  - Self-contained role management

## Docker
Memebot has a straightforward Docker image that can be build based on the [Dockerfile](./Dockerfile) in this 
repository. This image can be used for both deployment and testing purposes.
