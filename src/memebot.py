import json
import re
import shlex

import discord
import twitter

from commands.commands import Commands, SideEffects
from lib import constants


class MemeBot(discord.Client):
    """
    The main class that operates MemeBot, and directly controls all listeners
    """

    def __init__(self, **args):
        super().__init__(**args)

        twitter_api = twitter.Api(
            twitter_tokens['consumer_key'],
            twitter_tokens['consumer_secret'],
            twitter_tokens['access_token_key'],
            twitter_tokens['access_token_secret'],
            tweet_mode='exended'
        )

    async def on_ready(self) -> None:
        """
        Determines what the bot does as soon as it is logged into discord
        :return: None
        """
        print(f'Logged in as {self.user}')

    async def on_message(self, message: discord.message.Message) -> None:
        """
        Maintains all basic per-message functions of the bot, including extracting and executing !commands and
        updating databases with new data
        :param message: The most recent message sent to the server
        :return: None
        """
        if message.author == self.user:
            # ignore messages sent by this bot (for now)
            return

        # convert curly quotes to straight quotes
        message.content = message.content.replace('“','"').replace('”','"')

        # Iterate through each word in the message, and checks each one if
        # the "word" in the message is a twitter URL
        for content in message.content.split():
            if self.has_twitter(content):
                twitter_url = content
                
                # Because a twitter URL to a status is oftentimes as follows:
                # https://twitter.com/USER/status/xxxxxxxxxxxxxxxxxxx?s=yy
                # We need to split up the URL by the "/", and then split it up
                # again by the "?" in order to get the ID of the tweet being
                # linked
                tweet_id = twitter_url.split("/")[-1].split("?")[0]
                tweet_info = self.twitter_api.GetStatus(tweet_id)

                if tweet_info.media and len(tweet_info.media)>1:
                    emoji = ":" + str(len(tweet_info.media)) + ":"
                    await message.add_reaction(constants.EMOJI_MAP[emoji])

                if tweet_info.quoted_status:
                    quote_tweet_urls = self.get_tweet_urls(tweet_info)
                    if quote_tweet_urls != "":
                        await message.channel.send(quote_tweet_urls)

        if self.is_command(message.content):
            try:
                command, *args = shlex.split(message.content)
            except ValueError as e:
                await message.channel.send('Could not parse command: ' + str(e))
                return

            result = await Commands.execute(command, args, self, message)
            new_message = await message.channel.send(**result.kwargs)
            await SideEffects.borrow(new_message)

    def is_command(self, msg: str) -> bool:
        """Returns True if msg is a command, otherwise returns False."""
        # re.match looks for a match anywhere in msg. Regex matches if first
        # word of msg is ! followed by letters. 
        return bool(re.match(r'^![a-zA-Z]+(\s|$)', msg))

    def has_twitter(self, msg: str) -> bool:
        """Returns true if msg is a twitter link, otherwise returns False"""
        # re.match looks for a match in msg. Regex Matches if first part of msg
        # is https://twitter.com/XXXXXXXXXXXXXX
        return bool(re.match(r'https:\/\/twitter\.com\b[-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*', msg))

    def get_tweet_urls(self, tweet_info: twitter.models.Status) -> str:
        """
        Gets URLs of quoteted tweets (max 3)
        :param tweet_info: information of tweet
        :return: URL of media/quote tweet(s)
        """
        tweets = ""
        for level in range(3):
            tweets = tweets + " https://twitter.com/i/web/status/" + tweet_info.quoted_status.id_str
            tweet_info = self.twitter_api.GetStatus(tweet_info.quoted_status.id)
            if not tweet_info.quoted_status:
                break
        return tweets
