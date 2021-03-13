import json
import re

import discord
import tweepy

import commands
import config
from lib import constants


class MemeBot(discord.Client):
    """
    The main class that operates MemeBot, and directly controls all listeners
    """

    def __init__(self, **args):
        super().__init__(**args, intents=discord.Intents().all())

        with open(config.twitter_api_tokens) as twitter_api_tokens:
            twitter_tokens = json.load(twitter_api_tokens)

        self.twitter_api = tweepy.API(
            tweepy.AppAuthHandler(twitter_tokens['consumer_key'], twitter_tokens['consumer_secret']))

        self.twitter_url_pattern = re.compile(
            r'.*(https://twitter\.com/([0-9a-zA-Z_]+|i/web)/status/[0-9]+(\?s=\d+)?).*')

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
        twitter_url = self.get_twitter_url_from_message(message.content)
        if twitter_url:

            """Because a twitter URL to a status is oftentimes as follows:
            https://twitter.com/USER/status/xxxxxxxxxxxxxxxxxxx?s=yy
            We need to split up the URL by the "/", and then split it up
            again by the "?" in order to get the ID of the tweet being
            linked"""
            tweet_id = twitter_url.split("/")[-1].split("?")[0]
            tweet_info = self.twitter_api.get_status(tweet_id)
            tweet_media = tweet_info.extended_entities['media'] if 'media' in tweet_info.entities else []

            if len(tweet_media) > 1:
                emoji = ":" + str(len(tweet_media)) + ":"
                await message.add_reaction(constants.EMOJI_MAP[emoji])

            if tweet_info.is_quote_status:
                quote_tweet_urls = self.get_quote_tweet_urls(tweet_info)
                await message.channel.send(quote_tweet_urls)

    def get_twitter_url_from_message(self, content: str) -> str:
        """
        Loops through each "word" in conetnt, compares the word to a regex
        and returns the "word" in the message that matches the twitter URL regex
        :param content: message that was sent in discord
        """
        match = self.twitter_url_pattern.match(content)
        if match:
            return match.groups()[0]
        else:
            return ""

    def get_quote_tweet_urls(self, tweet_info: tweepy.models.Status) -> str:
        """
        Gets URLs of quoteted tweets (nested up to max 3)
        :param tweet_info: information of tweet
        :return: URL of media/quote tweet(s)
        """
        tweets = "quoted tweet(s): "
        for _ in range(3):
            tweets += "\nhttps://twitter.com/" + tweet_info.quoted_status.author.screen_name + "/status/" + tweet_info.quoted_status.id_str
            tweet_info = self.twitter_api.get_status(tweet_info.quoted_status.id)
            if not tweet_info.is_quote_status:
                break
        return tweets


client: discord.Client = MemeBot()
