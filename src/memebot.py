import json
import re
from typing import Optional

import discord
import twitter

import commands
from lib import constants


class MemeBot(discord.Client):
    """
    The main class that operates MemeBot, and directly controls all listeners
    """

    def __init__(self, **args):
        super().__init__(**args, intents=discord.Intents().all())
        global client
        if client is not None:
            raise ReferenceError("There can only be one Memebot!")
        client = self

        with open('twitter_api_tokens.json') as twitter_api_tokens:
            twitter_tokens = json.load(twitter_api_tokens)

        self.twitter_api = twitter.Api(
                twitter_tokens['consumer_key'],
                twitter_tokens['consumer_secret'],
                twitter_tokens['access_token_key'],
                twitter_tokens['access_token_secret'],
                tweet_mode='extended'
            )
        
        self.twitter_url_pattern = re.compile(r'https:\/{2}twitter\.com\/([0-9a-zA-Z_]+|i\/web)\/status\/[0-9]+(\?s=\d+)?')

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
        if message.author == self.user:
            # ignore messages sent by this bot (for now)
            return
        else:
            await commands.execution.execute_if_command(message)

        # Iterate through the message sent, and check if the message conatined
        # a "word" that was a twitter URL to a status.
        twitter_url = self.get_twitter_url(message.content)
        if twitter_url:

            """Because a twitter URL to a status is oftentimes as follows:
            https://twitter.com/USER/status/xxxxxxxxxxxxxxxxxxx?s=yy
            We need to split up the URL by the "/", and then split it up
            again by the "?" in order to get the ID of the tweet being
            linked"""
            tweet_id = twitter_url.split("/")[-1].split("?")[0]
            tweet_info = self.twitter_api.GetStatus(tweet_id)

            if tweet_info.media and len(tweet_info.media) > 1:
                emoji = ":" + str(len(tweet_info.media)) + ":"
                await message.add_reaction(constants.EMOJI_MAP[emoji])

            if tweet_info.quoted_status:
                quote_tweet_urls = self.get_tweet_urls(tweet_info)
                if quote_tweet_urls != "":
                    await message.channel.send(quote_tweet_urls)

    def get_twitter_url(self, content: str) -> str:
        """
        Loops through each "word" in conetnt, compares the word to a regex
        and returns the "word" in the message that matches the twitter URL regex
        :param content: message that was sent in discord
        """
        for word in content.split():
            if self.twitter_url_pattern.match(word):
                return word
        return ""

    def get_tweet_urls(self, tweet_info: twitter.models.Status) -> str:
        """
        Gets URLs of quoteted tweets (max 3)
        :param tweet_info: information of tweet
        :return: URL of media/quote tweet(s)
        """
        tweets = "quoted tweet(s): "
        for level in range(3):
            tweets += "\n https://twitter.com/i/web/status/" + tweet_info.quoted_status.id_str
            tweet_info = self.twitter_api.GetStatus(tweet_info.quoted_status.id)
            if not tweet_info.quoted_status:
                break
        return tweets


client: Optional[discord.Client] = None
