# Memebot 

This is Memebot, a discord bot.

If you are hosting yourself, you will need to pass a Discord API client token to the bot
as a string, either via a command-line parameter or an environment variable. 
See [Configuration](#configuration) for more context.

## Configuration

### Command-line parameters

```
usage: main.py [-h] [--discord-api-token DISCORD_API_TOKEN]
               [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL} | -v]
               [--log-location {stdout,stderr,syslog,/path/to/file}] [--nodb]
               [--database-uri DATABASE_URI]
               [--clearurls-rules-url CLEARURLS_RULES_URL]
               [--clearurls-rules-refresh-hours CLEARURLS_RULES_REFRESH_HOURS]

options:
  -h, --help            show this help message and exit
  --discord-api-token DISCORD_API_TOKEN
                        The Discord API client token
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set logging level
  -v, --verbose         Use verbose logging. Equivalent to --log-level DEBUG
  --log-location {stdout,stderr,syslog,/path/to/file}
                        Set the location for MemeBot's log
  --nodb                Disable the database connection, and all features
                        which require it.
  --database-uri DATABASE_URI
                        URI of the MongoDB database server
  --clearurls-rules-url CLEARURLS_RULES_URL
                        URL from which to download ClearURLs rules
  --clearurls-rules-refresh-hours CLEARURLS_RULES_REFRESH_HOURS
                        Number of hours to wait between (lazy) refreshes of
                        ClearURLs rules
```

### Environment Variables
Memebot can also be configured with environment variables, although command-line arguments
will take precedence.

To see which environment variables can be used to configure Memebot, see [template.env](./docker/template.env).

## Commands

Current commands that can be used in Discord:

    /hello    - Say "hello" to Memebot!
    /help     - Learn how to use Memebot
    /paywall  - Remove paywall from a link *
    /role     - Self-contained role management
    /trackers - Remove tracking metadata from a link *

\*Can also be performed as a context menu action

## Development

### Virtual Environment

Memebot can be tested and run through a virtual environment. This is the recommended
approach for ensuring your [LSP](https://en.wikipedia.org/wiki/Language_Server_Protocol)
has access to the projects dependencies.

You can use any tools to create the virtual environment, but the ones officially supported
by the project are [`pip`](https://pypi.org/project/pip/) and [`uv`](https://docs.astral.sh/uv/).

```shell
# pip
$ python -m venv .venv
$ source .venv/bin/activate
$ python -m pip install -r pylock.toml

# uv
$ uv sync
```

### Docker
Memebot has a straightforward Docker image that can be built based on the [Dockerfile](./docker/Dockerfile) in this 
repository. This image can be used for both deployment and testing purposes.

To run Memebot:

```shell
$ docker compose up
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

Memebot has a suite of unit tests based on [`pytest`](https://pytest.org). The test code
is located in the [tests](./tests) directory. Running the tests is straightforward:

```shell
$ uv run pytest [/path/to/test/package/or/module]

# OR with venv activated

$ python -m pytest [/path/to/test/package/or/module]
```

Running the above from the root of the repository with no path(s) specified will run 
all the tests.

The tests can also be run from the _test_ Docker image:

```shell
$ docker run --rm -it memebot:test uv run pytest [/path/to/test/package/or/module]

# OR

$ docker-compose run -it bot uv run pytest [/path/to/test/package/or/module]
```

## Linting/Formatting

### `pre-commit`

This project optionally supports pre-commit to check your commits before they fail CI.
Hooks can be installed like so, and will check your code automatically every time you attempt to commit:

```shell
uv run pre-commit install
```

### Static Type Checker

Memebot uses static type checking from [`zuban`](https://zubanls.com) to improve code correctness. The config
for zuban is in [pyproject.toml](pyproject.toml). Most warnings and errors are enabled. 

To run `zuban`:

```shell
$ uv run zuban check
```

`zuban` can also function as an [LSP server]( locally) for your editor.

### Code Quality

Memebot uses several linters/formatters to ensure consistent code quality.

#### Python

```shell
# lint
uv run ruff check --fix
# format
uv run ruff format
```

#### TOML

```shell
# lint
uv run tombi check
# format
uv run tombi format
```

#### YAML

```shell
uv run yamllint .
```

#### Dockerfile

```shell
uv run hadolint docker/Dockerfile
```
