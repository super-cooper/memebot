# Memebot 

This is Memebot, a discord bot.

If you are hosting yourself, you will need to pass a Discord API client token to the bot
as a string, either via a command-line parameter or an environment variable. 
See [Configuration](#configuration) for more context.

## Configuration

### Command-line parameters

```
usage: main.py [-h] [--discord-api-token DISCORD_API_TOKEN]
               [--twitter-api-consumer-key TWITTER_API_CONSUMER_KEY]
               [--twitter-api-consumer-secret TWITTER_API_CONSUMER_SECRET]
               [--twitter-api-bearer-token TWITTER_API_BEARER_TOKEN]
               [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL} | -v]
               [--log-location {stdout,stderr,syslog,/path/to/file}]
               [--no-twitter] [--nodb] [--database-uri DATABASE_URI]

optional arguments:
  -h, --help            show this help message and exit
  --discord-api-token DISCORD_API_TOKEN
                        The Discord API client token
  --twitter-api-consumer-key TWITTER_API_CONSUMER_KEY
                        (DEPRECATED) The Twitter API consumer key
  --twitter-api-consumer-secret TWITTER_API_CONSUMER_SECRET
                        (DEPRECATED) The Twitter API consumer secret
  --twitter-api-bearer-token TWITTER_API_BEARER_TOKEN
                        The Twitter API OAuth 2.0 bearer token
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set logging level
  -v, --verbose         Use verbose logging. Equivalent to --log-level DEBUG
  --log-location {stdout,stderr,syslog,/path/to/file}
                        Set the location for MemeBot's log
  --no-twitter          Disable Twitter integration
  --nodb                Disable the database connection, and all features
                        which require it.
  --database-uri DATABASE_URI
                        URI of the MongoDB database server
```

### Environment Variables
Memebot can also be configured with environment variables, although command-line arguments
will take precedence.

To see which environment variables can be used to configure Memebot, see [template.env](./docker/template.env).

## Commands

Current commands that can be used in Discord:

    !hello - Say "hello" to Memebot!
    !help  - Learn how to use Memebot
    !poll  - Create a simple poll.
    !role  - Self-contained role management

## Docker
Memebot has a straightforward Docker image that can be build based on the [Dockerfile](./docker/Dockerfile) in this 
repository. This image can be used for both deployment and testing purposes.

The Memebot image is designed to be used as an "executable," since it is only designed to
run Memebot and nothing else. 

For example:
```shell
$ docker run --env-file docker/.env --rm -it memebot --discord-api-token ...
```

The Memebot image has two build targets: `release` and `test`. 

`release` contains only the dependencies to run Memebot, and only copies the source
directory. The `test` target has testing dependencies installed, and copies in the entire
repository. The default target is `test`, as it is the most convenient for development
and testing. `release` produces a slightly slimmer image which is only used for deployment. 

The easiest way to create your `.env` is by copying [template.env](./docker/template.env), 
and then filling out whichever environment variables are desired. 
Leaving variables empty just means that default values will be used.

## Tests

### mypy

Memebot uses static type checking from [mypy](http://mypy-lang.org) to improve code correctness. The config
for mypy is in [pyproject.toml](pyproject.toml). Most warnings and errors are enabled. 

To run mypy locally, ensure it is installed to the same python environment as all of your
Memebot dependencies, and then run it using the proper interpreter. 

```shell
$ venv/bin/mypy memebot

# OR

$ source venv/bin/activate
$ mypy memebot
```

To run mypy in Docker, ensure you are using an image built from the `test` target. 

```shell
$ docker run --rm -it --entrypoint mypy memebot:test memebot

# OR

$ docker-compose run --rm --entrypoint mypy bot memebot
```

You can speed up subsequent runs of mypy by mounting the `.mypy-cache` directory as a volume.
This way, mypy can reuse the cache it generates inside the container on the next run. 

```shell
$ docker run --rm --volume "$(pwd)/.mypy_cache:/opt/memebot/.mypy_cache" --entrypoint mypy -it memebot:test memebot

# OR

$ docker-compose run --rm --volume "$(pwd)/.mypy_cache:/opt/memebot/.mypy_cache" --entrypoint mypy bot memebot
```
