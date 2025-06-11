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
    command = interaction.command
    if not isinstance(command, discord.app_commands.Command):
        log.critical(
            "Non-command error handled by command error handler!", exc_info=error
        )
        return

    invocation = util.parse_invocation(interaction)

    if isinstance(error, exception.MemebotInternalError):
        # For intentionally thrown internal errors
        log.interaction(
            interaction,
            f"Raised an internal exception: ",
            level=logging.WARNING,
            exc_info=error,
        )
        err_msg = f"Internal error occurred with `{invocation}`"
    elif isinstance(error, exception.MemebotUserError):
        # If the error is user-facing, we want to send it directly to the user
        err_msg = str(error)
        log.interaction(interaction, err_msg)
    else:
        # For uncaught exceptions
        # (discord.py wraps these in a CommandInvokeError and re-raises)
        if isinstance(error, discord.app_commands.CommandInvokeError):
            original = error.original
        else:
            original = error
        log.interaction(
            interaction,
            f"Raised an unhandled exception: ",
            exc_info=original,
            level=logging.ERROR,
        )
        err_msg = f"Unhandled error occurred with `{invocation}`"

    await interaction.response.send_message(
        err_msg,
        ephemeral=True,
    )


@functools.cache
def get_memebot() -> discord.ext.commands.Bot:
    new_memebot = discord.ext.commands.Bot(
        command_prefix="/",
        intents=discord.Intents().all(),
        activity=discord.Game(name="• /hello"),
    )

    new_memebot.tree.add_command(commands.hello)
    new_memebot.tree.add_command(commands.role)
    new_memebot.tree.add_command(commands.paywall)
    new_memebot.tree.add_command(commands.paywall_context_menu)

    new_memebot.add_listener(on_ready)
    new_memebot.add_listener(on_interaction)
    new_memebot.tree.error(on_command_error)

    return new_memebot
