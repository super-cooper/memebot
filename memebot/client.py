import functools
import logging

import discord
import discord.ext.commands

from memebot import commands
from memebot import config
from memebot import db
from memebot import log
from memebot.lib import exception, util


async def on_ready() -> None:
    """
    Determines what the bot does as soon as it is logged into discord
    """
    memebot = get_memebot()
    if not memebot.user:
        raise exception.MemebotInternalError("Memebot is not logged in to Discord")
    log.info(f"Logged in as {memebot.user}")
    synced = await memebot.tree.sync()
    log.info(f"Synced {len(synced)} command(s)")
    if config.database_enabled:
        db_online = db.test()
        if db_online:
            log.info("Connected to database.")
        else:
            log.error("Could not connect to database.")


async def on_interaction(interaction: discord.Interaction) -> None:
    """
    Provides logging on interaction ingress
    """
    log.interaction(
        interaction,
        f"{util.parse_invocation(interaction)} from {interaction.user}",
    )


async def on_command_error(
    interaction: discord.Interaction, error: discord.app_commands.AppCommandError
) -> None:
    match interaction.command:
        case None:
            log.critical(
                "Non-command error handled by command error handler!", exc_info=error
            )
            return
        case discord.app_commands.Command():
            invocation = util.parse_invocation(interaction)
        case _:
            invocation = interaction.command.name

    match error:
        case exception.MemebotInternalError():
            # For intentionally thrown internal errors
            log.interaction(
                interaction,
                f"Raised an internal exception: ",
                level=logging.WARNING,
                exc_info=error,
            )
            err_msg = f"Internal error occurred with `{invocation}`"
        case exception.MemebotUserError():
            # If the error is user-facing, we want to send it directly to the user
            err_msg = str(error)
            log.interaction(interaction, err_msg)
        case _:
            # For uncaught exceptions
            # (discord.py wraps these in a CommandInvokeError and re-raises)
            if isinstance(error, discord.app_commands.CommandInvokeError):
                exc_info = error.original
            else:
                exc_info = error
            log.interaction(
                interaction,
                f"Raised an unhandled exception: ",
                exc_info=exc_info,
                level=logging.ERROR,
            )
            err_msg = f"Unhandled error occurred with `{invocation}`"

    await interaction.response.send_message(err_msg, ephemeral=True)


@functools.cache
def get_memebot() -> discord.ext.commands.Bot:
    new_memebot = discord.ext.commands.Bot(
        command_prefix="/",
        intents=discord.Intents().all(),
        activity=discord.Game(name="• /hello"),
    )

    commands.register_commands(new_memebot)

    new_memebot.add_listener(on_ready)
    new_memebot.add_listener(on_interaction)
    new_memebot.tree.error(on_command_error)

    return new_memebot
