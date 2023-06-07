from typing import Any
from unittest import mock

import pytest


@pytest.fixture
def mock_twitter_url() -> str:
    return "https://twitter.com/dril/status/922321981"


@pytest.fixture
@mock.patch("tweepy.ReferencedTweet")
def mock_referenced_tweet(MockReferencedTweet: type[mock.Mock]) -> mock.Mock:
    return MockReferencedTweet()


@pytest.fixture
@mock.patch("tweepy.ReferencedTweet")
def mock_referenced_tweet_2(MockReferencedTweet: type[mock.Mock]) -> mock.Mock:
    return MockReferencedTweet()


@pytest.fixture
@mock.patch("tweepy.ReferencedTweet")
def mock_referenced_tweet_3(MockReferencedTweet: type[mock.Mock]) -> mock.Mock:
    return MockReferencedTweet()


@pytest.fixture
@mock.patch("tweepy.ReferencedTweet")
def mock_referenced_tweet_4(MockReferencedTweet: type[mock.Mock]) -> mock.Mock:
    return MockReferencedTweet()


@pytest.fixture
@mock.patch("tweepy.Tweet", spec=True)
def mock_tweet(MockTweet: type[mock.Mock], mock_twitter_user: mock.Mock) -> mock.Mock:
    tweet = MockTweet()
    tweet.referenced_tweets = []
    tweet.author_id = mock_twitter_user.id
    return tweet


@pytest.fixture
@mock.patch("tweepy.Tweet", spec=True)
def mock_quote_tweet(
    MockTweet: type[mock.Mock],
    mock_referenced_tweet: mock.Mock,
    mock_twitter_user: mock.Mock,
) -> mock.Mock:
    tweet = MockTweet()
    mock_referenced_tweet.type = "quoted"
    tweet.referenced_tweets = [mock_referenced_tweet]
    tweet.author_id = mock_twitter_user.id
    return tweet


@pytest.fixture
@mock.patch("tweepy.Tweet", spec=True)
def mock_quote_tweet_2(
    MockTweet: mock.Mock,
    mock_referenced_tweet_2: mock.Mock,
    mock_twitter_user: mock.Mock,
) -> mock.Mock:
    tweet = MockTweet()
    mock_referenced_tweet_2.type = "quoted"
    tweet.referenced_tweets = [mock_referenced_tweet_2]
    tweet.author_id = mock_twitter_user.id
    return tweet


@pytest.fixture
@mock.patch("tweepy.Tweet", spec=True)
def mock_quote_tweet_3(
    MockTweet: mock.Mock,
    mock_referenced_tweet_3: mock.Mock,
    mock_twitter_user: mock.Mock,
) -> mock.Mock:
    tweet = MockTweet()
    mock_referenced_tweet_3.type = "quoted"
    tweet.referenced_tweets = [mock_referenced_tweet_3]
    tweet.author_id = mock_twitter_user.id
    return tweet


@pytest.fixture
@mock.patch("tweepy.Tweet", spec=True)
def mock_quote_tweet_4(
    MockTweet: mock.Mock,
    mock_referenced_tweet_4: mock.Mock,
    mock_twitter_user: mock.Mock,
) -> mock.Mock:
    tweet = MockTweet()
    mock_referenced_tweet_4.type = "quoted"
    tweet.referenced_tweets = [mock_referenced_tweet_4]
    tweet.author_id = mock_twitter_user.id
    return tweet


@pytest.fixture
@mock.patch("tweepy.User", new_callable=mock.MagicMock)
def mock_twitter_user(MockTwitterUser: type[mock.Mock]) -> mock.Mock:
    return MockTwitterUser()


@pytest.fixture
@mock.patch("tweepy.Response", autospec=True)
@mock.patch("tweepy.Client", autospec=True)
def mock_twitter_client(
    MockTwitterClient: type[mock.Mock],
    MockTwitterResponse: type[mock.Mock],
    mock_twitter_user: mock.Mock,
    mock_tweet: mock.Mock,
    mock_quote_tweet: mock.Mock,
    mock_quote_tweet_2: mock.Mock,
    mock_quote_tweet_3: mock.Mock,
    mock_quote_tweet_4: mock.Mock,
) -> mock.Mock:
    def _get_tweet(tweet_id: str, *_: Any, **__: Any) -> mock.Mock:
        resp = MockTwitterResponse()
        resp.data = next(
            (
                t
                for t in (
                    mock_quote_tweet,
                    mock_quote_tweet_2,
                    mock_quote_tweet_3,
                    mock_quote_tweet_4,
                )
                if t.id == tweet_id
            ),
            mock_tweet,
        )
        resp.includes = {"users": [mock_twitter_user]}
        return resp

    client = MockTwitterClient()
    client.get_tweet = _get_tweet
    return client
