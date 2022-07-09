"""
This is a module for managing our integration with Twitter. It owns all metadata related to Twitter, and the only state
it maintains is whether or not the API has been initialized.

All functions that make any network communication, except for init, should be asynchronous and stateless.
"""
import asyncio
import re
from typing import Tuple

import discord
import tweepy

import config
from lib import constants, util

# Regular expression that describes the pattern of a Tweet URL
twitter_url_pattern = re.compile(r'https://twitter\.com/([0-9a-zA-Z_]+|i/web)/status/[0-9]+(\?s=\d+)?')

# Twitter API handle
twitter_api: tweepy.API

# Current bot user
bot_user: discord.ClientUser


def init(user: discord.ClientUser) -> None:
    """
    Authenticates to the Twitter API. This function is left synchronous, as any further interaction with Twitter
    depends on this function executing and returning successfully, and it should only be run once at startup.
    :param user: The user object for the bot user.
    """
    global twitter_api
    global bot_user
    twitter_api = tweepy.API(tweepy.AppAuthHandler(config.twitter_api_consumer_key, config.twitter_api_consumer_secret))
    bot_user = user


def get_twitter_api() -> tweepy.API:
    """
    Utility function for acquiring the module's API object, as to skip the null-checking
    :raises ValueError: If init() has not yet been called, making _twitter_api None
    :return: _twitter_api, if it has been initialized.
    """
    if twitter_api is None:
        raise ValueError("Twitter integration module has not yet been initialized.")
    return twitter_api


def get_twitter_url_from_message_content(content: str) -> Tuple[str, bool]:
    """
    Loops through each "word" in content, compares the word to a regex
    and returns the "word" in the message that matches the twitter URL regex
    :param content: message that was sent in discord
    """
    match = twitter_url_pattern.search(content)
    if match:
        return match[0], util.is_spoil(content, match.start())
    else:
        return "", False


def get_quote_tweet_urls(tweet_info: tweepy.models.Status, spoiled: bool) -> str:
    """
    Gets URLs of quoteted tweets (nested up to max 3)
    :param tweet_info: information of tweet
    :param spoiled: whether the quote tweets should be spoiled
    :return: URL of media/quote tweet(s)
    """
    tweets = "quoted tweet(s): "
    for _ in range(3):
        tweets += util.maybe_make_link_spoiler(
            f"\nhttps://twitter.com/{tweet_info.quoted_status.author.screen_name}"
            f"/status/{tweet_info.quoted_status.id_str}",
            spoiled,
        )
        tweet_info = get_twitter_api().get_status(tweet_info.quoted_status.id)
        if not tweet_info.is_quote_status:
            break
    return tweets


async def process_message_for_interaction(message: discord.Message) -> None:
    """
    Processes non-command content of a message to determine if a message contains Tweet information and requires
    interaction from MemeBot. Note that this will still affect command messages, but the content is not processed
    as a command by this function.
    :param message: The message to process
    """
    # Iterate through the message sent, and check if the message contained
    # a "word" that was a twitter URL to a status.
    twitter_url, spoiled = get_twitter_url_from_message_content(message.content)
    if twitter_url:
        # Because a twitter URL to a status is oftentimes as follows:
        # https://twitter.com/USER/status/xxxxxxxxxxxxxxxxxxx?s=yy
        # We need to split up the URL by the "/", and then split it up again by the "?" in order to get
        # the ID of the tweet being linked
        tweet_id = twitter_url.split("/")[-1].split("?")[0]
        tweet_info = get_twitter_api().get_status(tweet_id)
        tweet_media = tweet_info.extended_entities['media'] if 'media' in tweet_info.entities else []

        # React with a numeric emoji to Tweets containing multiple images
        if len(tweet_media) > 1:
            emoji = ":" + str(len(tweet_media)) + ":"
            asyncio.create_task(message.add_reaction(constants.EMOJI_MAP[emoji]))
        elif len(tweet_media) == 1 and 'video_info' in tweet_media[0]:
            # The media_url of a media dict is actually a thumbnail
            # To get the video, we have to pull it out of its video_info
            # We will choose the variant with the highest bitrate
            video_url = max(tweet_media[0]['video_info']['variants'], key=lambda v: int(v.get('bitrate', -1)))['url']
            asyncio.create_task(message.channel.send(f"embedded video:\n{util.maybe_make_link_spoiler(video_url, spoiled)}"))

        # Post quote tweet links.
        if tweet_info.is_quote_status and message.author != bot_user:
            quote_tweet_urls = get_quote_tweet_urls(tweet_info, spoiled)
            asyncio.create_task(message.channel.send(quote_tweet_urls))
