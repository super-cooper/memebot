import re
import shlex
import json

import discord
import twitter

from commands.commands import Commands, SideEffects


class MemeBot(discord.Client):
    """
    The main class that operates MemeBot, and directly controls all listeners
    """
    with open('python_tokens.json') as python_tokens:
        tokens = json.load(python_tokens)

    t_api = twitter.Api(
        tokens['consumer_key'],
        tokens['consumer_secret'],
        tokens['access_token_key'],
        tokens['access_token_secret']
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
            await message.channel.send(self.get_tweet_urls(tweet_id, 0 , ""))

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

    def get_tweet_urls(self, tweet_id, level, tweets):
        """Gets data of a tweet and checks if the tweet contains urls"""
        if level == 3:
            return tweets
        else:
            tweet_info = self.t_api.GetStatus(tweet_id)
            
            if tweet_info.media:
                tweets += "media at level " + str(level) + ": "
                media_urls = ""
                for m in tweet_info.media:
                    if m.type == "video":
                        print(m.video_info)
                        for v in m.video_info["variants"]:
                            if v["content_type"] == "video/mp4":
                                media_urls += v["url"] + " "
                                break
                    media_urls += m.media_url_https + " "
                tweets = media_urls + "\n"

            if tweet_info.urls:
                quoted_tweet_url = tweet_info.urls[0].expanded_url 
                quoted_tweet_id = quoted_tweet_url.split("/")[-1]
                return self.get_tweet_urls(quoted_tweet_id, level+1, tweets + " " +quoted_tweet_url)

            return tweets
