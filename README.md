# Memebot 

This is MemeBot, a discord bot.

If you are hosting yourself, you will need to create a file in the root directory of your local repository called 
`client_token` and paste your Discord developer client token into that file. Nothing else should be in the file.
From there, to run the bot, simply run the following command from the root of the project:

```bash
python3 src/main.py
```

Current commands that can be used in Discord:
    
    !help  - display help text
    !hello - print "Hello!"
    !poll  - create a simple poll
    !role  - manage mentionable roles

## Docker
Memebot has a straightforward Docker image that can be build based on the [Dockerfile](./Dockerfile) in this 
repository. This image can be used for both deployment and testing purposes, although regular testing with it is not 
recommended, as the image has to be rebuilt any time a file is edited or a configuration is changed.
