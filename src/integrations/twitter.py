"""
This is a module for managing our integration with Twitter. It owns all metadata related to Twitter, and the only state
it maintains is whether or not the API has been initialized.

All functions that make any network communication, except for init, should be asynchronous and stateless.
"""
import asyncio
import re
from typing import Tuple

import discord
import emoji
import tweepy

import config
from lib import util

# Regular expression that describes the pattern of a Tweet URL
twitter_url_pattern = re.compile(
    r"https://twitter\.com/(\w+|i/web)/status/\d+(\?s=\d+)?"
)

# Twitter API handle
twitter_api: tweepy.Client

# Current bot user
bot_user: discord.ClientUser


def init(user: discord.ClientUser) -> None:
    """
    Authenticates to the Twitter API. This function is left synchronous, as any further
    interaction with Twitter depends on this function executing and returning
    successfully, and it should only be run once at startup.
    :param user: The user object for the bot user.
    """
    global twitter_api
    global bot_user
    twitter_api = tweepy.Client(bearer_token=config.twitter_api_bearer_token)
    bot_user = user


def get_twitter_api() -> tweepy.Client:
    """
    Utility function for acquiring the module's API object, as to skip the null-checking
    :raises ValueError: If init() has not yet been called, making _twitter_api None
    :return: _twitter_api, if it has been initialized.
    """
    if not twitter_api:
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


def fetch_tweet_with_expansions(
    tweet_id: str,
) -> tuple[tweepy.Tweet, list[tweepy.User], list[tweepy.Media]]:
    """
    Fetches a Tweet from the Twitter API, along with relevant user and media detail
    """
    # Fetch the Tweet and requested expansions
    response = get_twitter_api().get_tweet(
        tweet_id,
        media_fields=["url", "variants"],
        user_fields=["username"],
        expansions=["attachments.media_keys", "referenced_tweets.id.author_id"],
    )

    # Verify API response
    if not isinstance(response, tweepy.Response):
        raise TypeError(f"Unexpected Twitter API response type: ({type(response)})")
    tweet_info = response.data
    if not isinstance(tweet_info, tweepy.Tweet):
        raise TypeError(f"Unexpected response data: {tweet_info}")
    tweet_media = response.includes.get("media", [])
    tweet_users = response.includes.get("users", [])

    return tweet_info, tweet_users, tweet_media


def is_quote_tweet(tweet: tweepy.Tweet) -> bool:
    return tweet.referenced_tweets and any(
        ref.type == "quoted" for ref in tweet.referenced_tweets
    )


def get_quote_tweet_urls(root_tweet: tweepy.Tweet, spoiled: bool) -> str:
    """
    Gets URLs of quoteted tweets (nested up to max 3)
    :param root_tweet: information of tweet
    :param spoiled: whether the quote tweets should be spoiled
    :return: URL of quote tweet(s)
    """
    output_text = "quoted tweet(s): "
    parent_tweet = root_tweet
    for _ in range(3):
        # Find the ID of the Tweet quoted by the parent
        qt_ref = [t for t in parent_tweet.referenced_tweets if t.type == "quoted"][0]
        qt, qt_users, _ = fetch_tweet_with_expansions(qt_ref.id)
        qt_author = [u for u in qt_users if u.id == qt.author_id][0]
        output_text += util.maybe_make_link_spoiler(
            f"\nhttps://twitter.com/{qt_author.username}/status/{qt.id}",
            spoiled,
        )
        if not is_quote_tweet(qt):
            break
        parent_tweet = qt
    return output_text


async def process_message_for_interaction(message: discord.Message) -> None:
    """
    Processes non-command content of a message to determine if a message contains Tweet
    information and requires interaction from MemeBot. Note that this will still affect
    command messages, but the content is not processed
    as a command by this function.
    :param message: The message to process
    """
    # Iterate through the message sent, and check if the message contained
    # a "word" that was a twitter URL to a status.
    twitter_url, spoiled = get_twitter_url_from_message_content(message.content)
    if twitter_url:
        # Because a twitter URL to a status is oftentimes as follows:
        # https://twitter.com/USER/status/xxxxxxxxxxxxxxxxxxx?s=yy
        # We need to split up the URL by the "/", and then split it up again
        # by the "?" in order to get the ID of the tweet being linked
        tweet_id = twitter_url.split("/")[-1].split("?")[0]

        tweet_info, _, tweet_media = fetch_tweet_with_expansions(tweet_id)

        # React with a numeric emoji to Tweets containing multiple images
        if (n_images := len(tweet_media)) > 1:
            asyncio.create_task(
                message.add_reaction(emoji.emojize(f":keycap_{n_images}:"))
            )
        # For tweets containing only a single video, we embed the video in Discord.
        elif n_images == 1 and tweet_media[0].type in ("video", "animated_gif"):
            # The media_url of a media dict is actually a thumbnail
            # To get the video, we have to pull it out of its video_info
            # We will choose the variant with the highest bitrate
            video_url = max(
                tweet_media[0].data["variants"],
                key=lambda v: int(v.get("bitrate", -1)),
            )["url"]
            asyncio.create_task(
                message.channel.send(
                    f"embedded video:\n"
                    f"{util.maybe_make_link_spoiler(video_url, spoiled)}"
                )
            )

        # Post quote tweet links.
        if is_quote_tweet(tweet_info) and message.author != bot_user:
            quote_tweet_urls = get_quote_tweet_urls(tweet_info, spoiled)
            asyncio.create_task(message.channel.send(quote_tweet_urls))
