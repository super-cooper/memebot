import urllib.parse
from unittest import mock

import pytest

from memebot.integrations import clear_urls
from memebot.lib import exception


class TestClearURLsProvider:
    def test_matches(self):
        provider = clear_urls.ClearURLsProvider(
            provider="test_provider",
            url_pattern=r"^https?:\/\/example\.com",
            rule_patterns=None,
            raw_rule_patterns=None,
            referral_marketing_patterns=None,
            redirection_patterns=None,
            exception_patterns=[r"^https?:\/\/example\.com\/excluded"],
        )

        assert provider.matches("https://example.com/page") is True
        assert provider.matches("https://example.com/page?param=value") is True
        assert provider.matches("https://example.com/excluded") is False
        assert provider.matches("https://other-domain.com") is False

    def test_strip_params(self):
        provider = clear_urls.ClearURLsProvider(
            provider="test_provider",
            url_pattern=r"^https?:\/\/example\.com",
            rule_patterns=["utm_source", "utm_medium", "ref"],
            raw_rule_patterns=None,
            referral_marketing_patterns=None,
            redirection_patterns=None,
            exception_patterns=None,
        )

        url = "https://example.com/page?utm_source=test&utm_medium=social&id=123&ref=twitter"
        cleaned_url = provider.strip_params(url)

        parsed = urllib.parse.urlparse(cleaned_url)
        params = urllib.parse.parse_qs(parsed.query)

        assert "utm_source" not in params
        assert "utm_medium" not in params
        assert "ref" not in params
        assert "id" in params
        assert params["id"] == ["123"]

    def test_redirect(self):
        provider = clear_urls.ClearURLsProvider(
            provider="test_provider",
            url_pattern=r"^https?:\/\/example\.com",
            rule_patterns=None,
            raw_rule_patterns=None,
            referral_marketing_patterns=None,
            redirection_patterns=[r"^https?:\/\/example\.com\/redirect\?url=(.*)$"],
            exception_patterns=None,
        )

        redirect_url = "https://example.com/redirect?url=https%3A%2F%2Fdestination.com"
        result = provider.redirect(redirect_url)
        assert result == "https://destination.com"

        normal_url = "https://example.com/page"
        result = provider.redirect(normal_url)
        assert result == normal_url

    def test_clean(self):
        provider = clear_urls.ClearURLsProvider(
            provider="test_provider",
            url_pattern=r"^https?:\/\/example\.com",
            rule_patterns=["utm_source", "utm_medium"],
            raw_rule_patterns=None,
            referral_marketing_patterns=None,
            redirection_patterns=[r"^https?:\/\/example\.com\/redirect\?url=(.*)$"],
            exception_patterns=None,
        )

        with mock.patch.object(
            provider, "strip_params"
        ) as mock_strip_params, mock.patch.object(
            provider, "redirect"
        ) as mock_redirect:

            mock_strip_params.return_value = "https://example.com/stripped"
            mock_redirect.return_value = "https://destination.com"

            result = provider.clean("https://example.com/original")

            mock_strip_params.assert_called_once_with("https://example.com/original")
            mock_redirect.assert_called_once_with("https://example.com/stripped")
            assert result == "https://destination.com"


def test_decode_uri():
    encoded_uri = "https%3A%2F%2Fexample.com%2Fpath%3Fparam%3Dvalue"
    decoded_uri = clear_urls._decode_uri(encoded_uri)
    assert decoded_uri == "https://example.com/path?param=value"

    # Double encoding
    double_encoded = urllib.parse.quote(encoded_uri)
    decoded_uri = clear_urls._decode_uri(double_encoded)
    assert decoded_uri == "https://example.com/path?param=value"


def test_is_encoded_uri():
    assert clear_urls._is_encoded_uri("https%3A%2F%2Fexample.com") is True
    assert clear_urls._is_encoded_uri("https://example.com") is False


def test_strip_trackers():
    test_provider = clear_urls.ClearURLsProvider(
        provider="test_provider",
        url_pattern=r"^https?:\/\/example\.com",
        rule_patterns=["utm_source", "utm_medium", "ref"],
        raw_rule_patterns=None,
        referral_marketing_patterns=None,
        redirection_patterns=None,
        exception_patterns=None,
    )

    with mock.patch(
        "memebot.integrations.clear_urls.providers", [test_provider]
    ), mock.patch("memebot.integrations.clear_urls._refresh_providers"):

        # URL matches the provider
        url = "https://example.com/page?utm_source=test&id=123"
        stripped = clear_urls.strip_trackers(url)

        parsed = urllib.parse.urlparse(stripped)
        params = urllib.parse.parse_qs(parsed.query)
        assert "utm_source" not in params
        assert "id" in params

        # URL doesn't match any provider
        url = "https://other-domain.com/page?utm_source=test"
        stripped = clear_urls.strip_trackers(url)

        assert stripped == url


def test_strip_trackers_no_providers():
    # Mock empty provider list and ensure _refresh_providers doesn't add any
    with mock.patch.object(clear_urls, "providers", []), mock.patch.object(
        clear_urls, "_refresh_providers"
    ):

        url = "https://example.com/page?utm_source=test"

        # Should raise an exception when no providers are available
        with pytest.raises(exception.MemebotInternalError):
            clear_urls.strip_trackers(url)


def test_json_to_provider():
    provider_data = {
        "urlPattern": r"^https?:\/\/example\.com",
        "rules": ["utm_source", "utm_medium"],
        "redirections": [r"^https?:\/\/example\.com\/redirect\?url=(.*)$"],
    }

    provider = clear_urls._json_to_provider("test_provider", provider_data)

    assert provider.provider == "test_provider"
    assert len(provider.rules) == 2
    assert len(provider.redirections) == 1


def test_json_to_provider_invalid():
    # Missing urlPattern
    invalid_data = {"rules": ["utm_source"]}

    with mock.patch("memebot.log.exception") as mock_log_exc:
        result = clear_urls._json_to_provider("invalid_provider", invalid_data)
        assert result is None
        mock_log_exc.assert_called_once()


def test_convert_rules_to_providers():
    rules_json = r"""
    {
        "providers": {
            "test_provider": {
                "urlPattern": "^https?:\\/\\/example\\.com",
                "rules": ["utm_source", "utm_medium"]
            },
            "another_provider": {
                "urlPattern": "^https?:\\/\\/another\\.com",
                "rules": ["ref"]
            }
        }
    }
    """

    providers = clear_urls._convert_rules_to_providers(rules_json)

    assert len(providers) == 2 + len(clear_urls._CUSTOM_PROVIDERS)
    for custom_provider in clear_urls._CUSTOM_PROVIDERS:
        assert any(p.provider == custom_provider for p in providers)
    assert any(p.provider == "test_provider" for p in providers)
    assert any(p.provider == "another_provider" for p in providers)


def test_convert_rules_to_providers_invalid_without_existing_providers():
    with pytest.raises(exception.MemebotInternalError):
        clear_urls._convert_rules_to_providers("invalid json")

    with pytest.raises(exception.MemebotInternalError):
        clear_urls._convert_rules_to_providers('{"not_providers": {}}')
