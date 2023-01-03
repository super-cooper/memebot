import discord
import discord.ext.commands

import commands
import config
import db
import log
from integrations import twitter
from lib import exception, util
from typing import Optional, cast


async def on_ready() -> None:
    """
    Determines what the bot does as soon as it is logged into discord
    """
    if not memebot.user:
        raise exception.MemebotInternalError("Memebot is not logged in to Discord")
    log.info(f"Logged in as {memebot.user}")
    synced = await memebot.tree.sync()
    log.info(f"Synced {len(synced)} command(s)")
    if config.twitter_enabled:
        twitter.init(memebot.user)
    if config.database_enabled:
        db_online = db.test()
        if db_online:
            log.info("Connected to database.")
        else:
            log.error("Could not connect to database.")


async def on_command_error(
    interaction: discord.Interaction, error: discord.app_commands.AppCommandError
) -> None:
    command = interaction.command
    if not isinstance(command, discord.app_commands.Command):
        log.exception(error)
        return

    invocation = util.parse_invocation(interaction.data)

    if isinstance(error, exception.MemebotInternalError):
        # For intentionally thrown internal errors
        log.exception(f"`{invocation}` raised an internal exception: ", exc_info=error)
        err_msg = f"Internal error occurred with `{invocation}`"
    elif isinstance(error, discord.app_commands.CommandInvokeError):
        # For uncaught exceptions
        # (discord.py wraps these in a CommandInvokeError and re-raises)
        log.exception(
            f"`{invocation}` raised an unhandled exception: ", exc_info=error.original
        )
        err_msg = f"Unhandled error occurred with `{invocation}`"
    else:
        err_msg = str(error)

    await interaction.response.send_message(
        err_msg,
        ephemeral=True,
    )


memebot = discord.ext.commands.Bot(
    command_prefix="!",
    intents=discord.Intents().all(),
    activity=discord.Game(name="• /hello"),
)

memebot.tree.add_command(commands.hello)
memebot.tree.add_command(commands.poll)
memebot.tree.add_command(commands.role)

memebot.add_listener(on_ready)
memebot.tree.error(on_command_error)
if config.twitter_enabled:
    memebot.add_listener(twitter.process_message_for_interaction, "on_message")

run = memebot.run
