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
    with open('twitter_api_tokens.json') as twitter_api_tokens:
        twitter_tokens = json.load(twitter_api_tokens)

    twitter_api = twitter.Api(
        twitter_tokens['consumer_key'],
        twitter_tokens['consumer_secret'],
        twitter_tokens['access_token_key'],
        twitter_tokens['access_token_secret']
    )

    def __init__(self, **args):
        super().__init__(**args)

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

        if self.is_twitter(message.content):
            twitter_url, *args = shlex.split(message.content)
            tweet_id = twitter_url.split("/")[-1].split("?")[0]
            tweet_info = self.get_tweet_info(tweet_id)
            if tweet_info.media:
                emoji = self.get_tweet_media_count(tweet_info)
                if emoji > 1:
                    emoji = ":" +str(emoji)+ ":"
                    await message.add_reaction(constants.EMOJI_MAP[emoji])
            
            if tweet_info.urls:
                await message.channel.send(self.get_tweet_urls(tweet_id, 0, ""))

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

    def is_twitter(self, msg: str) -> bool:
        """Returns true if msg is a twitter link, otherwise returns False"""
        # re.match looks for a match in msg. Regex Matches if first part of msg
        # is https://twitter.com/XXXXXXXXXXXXXX
        return bool(re.match(r'https:\/\/twitter\.com\b[-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*', msg))

    def get_tweet_info(self, tweet_id: str) -> twitter.models.Status:
        """
        gets data from twitter API of a tweet ID
        :param tweet_id: ID of tweet in message:
        :return: data from twitter API
        """
        tweet_info = self.twitter_api.GetStatus(tweet_id)
        return tweet_info

    def get_tweet_media_count(self, tweet_info: twitter.models.Status) -> int:
        """
        counts number of media (images) in a tweet
        :param tweet_info: data of tweet from most recent message.
        :return: number of media in tweet
        """
        count = 0
        for media in tweet_info.media:
            count += 1
        
        return count

    def get_tweet_urls(self, tweet_id: str, level: int, tweets: str) -> str:
        """
        Gets data of a tweet and checks if the tweet contains URLs
        :param tweet_id: id of tweet
        :param level: current depth of quote tweet(s) (max 4)
        :param tweets: string of twitter URLs containing quote tweets
        :return: URL of media/quote tweet(s)
        """
        if level == 3:
            return tweets
        else:
            tweet_info = self.twitter_api.GetStatus(tweet_id)

            if tweet_info.urls:
                quoted_tweet_url = tweet_info.urls[0].expanded_url 
                quoted_tweet_id = quoted_tweet_url.split("/")[-1]
                return self.get_tweet_urls(quoted_tweet_id, level+1, tweets + " " +quoted_tweet_url)

            return tweets