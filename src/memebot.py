import discord.ext.commands.bot

import commands
import config
import db
import log
from integrations import twitter
from lib import exception


async def on_ready():
    """
    Determines what the bot does as soon as it is logged into discord
    """
    log.info(f"Logged in as {memebot.user}")
    if config.twitter_enabled:
        twitter.init(memebot.user)
    if config.database_enabled:
        db_online = db.test()
        if db_online:
            log.info("Connected to database.")
        else:
            log.error("Could not connect to database.")


async def on_command_error(ctx: discord.ext.commands.Context, error: Exception):
    invocation = f"{ctx.prefix}{' '.join(ctx.message.content.split())}"
    if isinstance(error, exception.MemebotInternalError):
        # For internal errors
        log.exception(f"`{invocation}` raised an internal exception: ", exc_info=error)
        await ctx.send(f"Internal error occurred with command `{invocation}`")
    elif isinstance(error, discord.ext.commands.CommandError):
        # For user-facing errors
        # This is the easiest way to attach the exception to the context such that the help command is able to access it
        ctx.kwargs["error"] = error
        await ctx.send_help(ctx.command)
    else:
        # For unhandled exceptions
        log.exception(f"`{invocation}` raised an unhandled exception: ", exc_info=error)
        await ctx.send(f"Internal error occurred with command `{invocation}`")


memebot = discord.ext.commands.Bot(command_prefix="!", help_command=commands.Help(), intents=discord.Intents().all(),
                                   activity=discord.Game(name="• !help"))

memebot.add_command(commands.hello)
memebot.add_command(commands.poll)
memebot.add_command(commands.role)

memebot.add_listener(on_ready)
memebot.add_listener(on_command_error)
if config.twitter_enabled:
    memebot.add_listener(twitter.process_message_for_interaction, "on_message")

run = memebot.run
