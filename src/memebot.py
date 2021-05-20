import asyncio

import discord

import commands
import config
import db
from integrations import twitter


class MemeBot(discord.Client):
    """
    The main class that operates MemeBot, and directly controls all listeners
    """

    def __init__(self, **args):
        super().__init__(**args, intents=discord.Intents().all())
        if config.twitter_enabled:
            twitter.init(config.twitter_api_tokens)
        db.test()

    async def on_ready(self) -> None:
        """
        Determines what the bot does as soon as it is logged into discord
        :return: None
        """
        print(f'Logged in as {self.user}')

    async def on_message(self, message: discord.Message) -> None:
        """
        Maintains all basic per-message functions of the bot, including extracting and executing !commands and
        updating databases with new data
        :param message: The most recent message sent to the server
        :return: None
        """
        # Ignore commands sent by this bot (for now).
        if message.author != self.user:
            await commands.execution.execute_if_command(message)

        asyncio.create_task(twitter.process_message_for_interaction(message))

        
client: discord.Client = MemeBot()
