from unittest import mock

import emoji
import pytest

from memebot.integrations import twitter
from memebot.lib import exception


def test_twitter_url_regex(mock_twitter_url: str) -> None:
    """
    Tests that the Twitter regex only works on valid tweet URLs
    """
    assert twitter.twitter_url_pattern.search(mock_twitter_url) is not None
    assert twitter.twitter_url_pattern.search(f"{mock_twitter_url}?s=19") is not None
    assert (
        twitter.twitter_url_pattern.search(f"{mock_twitter_url}?s=19&t=12345")
        is not None
    )
    assert twitter.twitter_url_pattern.search("https://memebot.com") is None
    assert twitter.twitter_url_pattern.search("https://twitter.com/foo/bar") is None
    assert (
        twitter.twitter_url_pattern.search("https://twitter.com/i/status/12345")
        is not None
    )
    assert (
        twitter.twitter_url_pattern.search("https://twitter.com/i/web/status/12345")
        is not None
    )
    assert twitter.twitter_url_pattern.search("https://twitter.com") is None
    assert twitter.twitter_url_pattern.search("twitter.com") is None
    assert twitter.twitter_url_pattern.search("twitter.com/i/status/12345") is None


def test_get_twitter_url_from_message_content(mock_twitter_url: str) -> None:
    """
    Test that we're able to successfully pull a Tweet URL from a discord message
    """
    assert twitter.get_twitter_url_from_message_content(
        f"foo bar baz {mock_twitter_url} 1 2 3"
    ) == (mock_twitter_url, False)
    assert twitter.get_twitter_url_from_message_content(
        f"foo bar baz {mock_twitter_url}"
    ) == (mock_twitter_url, False)
    assert twitter.get_twitter_url_from_message_content(
        f"{mock_twitter_url} 1 2 3"
    ) == (mock_twitter_url, False)

    # Test spoiler
    assert twitter.get_twitter_url_from_message_content(
        f"foo bar baz ||{mock_twitter_url}|| 1 2 3"
    ) == (mock_twitter_url, True)
    assert twitter.get_twitter_url_from_message_content(
        f"foo bar baz ||{mock_twitter_url}||"
    ) == (mock_twitter_url, True)
    assert twitter.get_twitter_url_from_message_content(
        f"||{mock_twitter_url}|| 1 2 3"
    ) == (mock_twitter_url, True)
    assert twitter.get_twitter_url_from_message_content(
        f"||foo bar baz {mock_twitter_url}|| 1 2 3"
    ) == (mock_twitter_url, True)


def test_is_quote_tweet(mock_quote_tweet: mock.Mock, mock_tweet: mock.Mock) -> None:
    """
    Test if we properly evaluate quote tweets
    """
    assert twitter.is_quote_tweet(mock_quote_tweet)
    assert not twitter.is_quote_tweet(mock_tweet)


def test_get_quote_tweet_urls(
    mock_quote_tweet: mock.Mock, mock_tweet: mock.Mock, mock_twitter_user: mock.Mock
) -> None:
    """
    Test if we properly construct the string which displays nested quote tweet URLs
    """
    actual = twitter.get_quote_tweet_urls(mock_quote_tweet, False)
    expected = (
        f"quoted tweet(s): \n"
        f"https://twitter.com/{mock_twitter_user.username}"
        f"/status/{mock_tweet.id}"
    )
    assert actual == expected


def test_nested_quote_tweet(
    mock_quote_tweet: mock.Mock,
    mock_quote_tweet_2: mock.Mock,
    mock_quote_tweet_3: mock.Mock,
    mock_quote_tweet_4: mock.Mock,
    mock_twitter_user: mock.Mock,
) -> None:
    """
    Test that multiple nested quote tweets come out properly
    """
    mock_quote_tweet.referenced_tweets[0].id = mock_quote_tweet_2.id
    mock_quote_tweet_2.referenced_tweets[0].id = mock_quote_tweet_3.id
    mock_quote_tweet_3.referenced_tweets[0].id = mock_quote_tweet_4.id
    actual = twitter.get_quote_tweet_urls(mock_quote_tweet, False)
    expected = (
        "quoted tweet(s): \n"
        f"https://twitter.com/{mock_twitter_user.username}"
        f"/status/{mock_quote_tweet_2.id}\n"
        f"https://twitter.com/{mock_twitter_user.username}"
        f"/status/{mock_quote_tweet_3.id}\n"
        f"https://twitter.com/{mock_twitter_user.username}"
        f"/status/{mock_quote_tweet_4.id}"
    )
    assert actual == expected


def test_quote_tweet_non_quote_failure(mock_tweet: mock.Mock) -> None:
    """
    Test that attempting to unroll a non-quote tweet fails
    """
    with pytest.raises(exception.MemebotInternalError):
        twitter.get_quote_tweet_urls(mock_tweet, False)


@pytest.mark.asyncio
@pytest.mark.parametrize("num_media", [2, 3, 4])
async def test_tweet_media_reaction(
    mock_twitter_url: str,
    mock_message: mock.Mock,
    num_media: int,
) -> None:
    """
    Tests that tweets with more than 1 media item get reacted to
    """
    old_get_tweet = twitter.twitter_api.get_tweet

    def patched_get_tweet(*args, **kwargs):
        response = old_get_tweet(*args, **kwargs)
        response.includes |= {"media": [mock.MagicMock()] * num_media}
        return response

    with mock.patch.object(twitter.twitter_api, "get_tweet", patched_get_tweet):
        mock_message.content = mock_twitter_url
        await twitter.process_message_for_interaction(mock_message)
        mock_message.add_reaction.assert_awaited_once_with(
            emoji.emojize(f":keycap_{num_media}:")
        )


@pytest.mark.asyncio
async def test_tweet_media_no_reaction(
    mock_twitter_url: str, mock_message: mock.Mock
) -> None:
    """
    Tests that tweets with a single piece of media do not get reacted to
    """
    old_get_tweet = twitter.twitter_api.get_tweet

    def patched_get_tweet(*args, **kwargs):
        response = old_get_tweet(*args, **kwargs)
        response.includes |= {"media": [mock.MagicMock()]}
        return response

    with mock.patch.object(twitter.twitter_api, "get_tweet", patched_get_tweet):
        mock_message.content = mock_twitter_url
        await twitter.process_message_for_interaction(mock_message)
        mock_message.add_reaction.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("media_type", ["video", "animated_gif"])
@pytest.mark.parametrize("content_type", ["video/mp4", "video/mpeg"])
async def test_tweet_embedded_video(
    mock_twitter_url: str, mock_message: mock.Mock, media_type: str, content_type: str
) -> None:
    """
    Tests that tweets with a video have the video embedded
    """
    old_get_tweet = twitter.twitter_api.get_tweet
    mock_variant_1 = mock.MagicMock()
    mock_variant_2 = mock.MagicMock()
    mock_variant_3 = mock.MagicMock()

    with mock.patch("tweepy.media.Media", spec=True) as MockMedia:

        def patched_get_tweet(*args, **kwargs):
            response = old_get_tweet(*args, **kwargs)
            mock_media = MockMedia()
            mock_media.type = media_type
            mock_media.variants = [
                {"bitrate": n, "url": variant, "content_type": content_type}
                for n, variant in enumerate(
                    (mock_variant_1, mock_variant_2, mock_variant_3)
                )
            ]
            response.includes |= {"media": [mock_media]}
            return response

        with mock.patch.object(twitter.twitter_api, "get_tweet", patched_get_tweet):
            mock_message.content = mock_twitter_url
            await twitter.process_message_for_interaction(mock_message)
            mock_message.channel.send.assert_awaited_once_with(
                f"embedded video:\n{mock_variant_3}"
            )


@pytest.mark.asyncio
async def test_single_media_no_embed(
    mock_message: mock.Mock, mock_twitter_url: str
) -> None:
    """
    Tests that a tweet with a single non-video media does not attempt to embed
    """
    old_get_tweet = twitter.twitter_api.get_tweet

    def patched_get_tweet(*args, **kwargs):
        response = old_get_tweet(*args, **kwargs)
        response.includes |= {"media": [mock.MagicMock()]}
        return response

    with mock.patch.object(twitter.twitter_api, "get_tweet", patched_get_tweet):
        mock_message.content = mock_twitter_url
        await twitter.process_message_for_interaction(mock_message)
        mock_message.channel.send.assert_not_awaited()
