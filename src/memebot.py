import discord
import discord.ext.commands

import commands
import config
import db
import log
from integrations import twitter
from lib import exception


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
        log.warning("Interaction not a command")
        return
    log.exception(f"`{command.name}` raised an unhandled exception: ", exc_info=error)
    await interaction.response.send_message(
        error,
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
