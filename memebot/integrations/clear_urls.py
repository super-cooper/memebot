import functools
import hashlib
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, UTC
from typing import cast

import pydantic

from memebot import config
from memebot import log
from memebot.lib import exception, util

_CUSTOM_PROVIDERS = {
    "vxtwitter": {
        "urlPattern": r"^https?:\/\/(?:[a-z0-9-]+\.)*?vxtwitter.com",
        "rules": [r"(?:ref_?)?src", r"s", r"cn", r"ref_url", r"t"],
        "exceptions": [r"^https?:\/\/vxtwitter.com\/i\/redirect"],
    },
    "fxtwitter": {
        "urlPattern": r"^https?:\/\/(?:[a-z0-9-]+\.)*?fxtwitter.com",
        "rules": [r"(?:ref_?)?src", r"s", r"cn", r"ref_url", r"t"],
        "exceptions": [r"^https?:\/\/fxtwitter.com\/i\/redirect"],
    },
}


_URI_ENCODED_CHARS_PATTERN = re.compile(r"%[0-9a-fA-F]{2}")


def _is_encoded_uri(uri: str) -> bool:
    return bool(_URI_ENCODED_CHARS_PATTERN.search(uri))


def _decode_uri(uri: str) -> str:
    # https://github.com/ClearURLs/Addon/blob/2d4711e548a65e5de30d71eabf9e7ae3a60d8cd0/core_js/tools.js#L243
    while _is_encoded_uri(uri):
        uri = urllib.parse.unquote(uri)
    return uri


class ClearURLsProvider:
    """
    Describes a provider pattern specified by the ClearURLs schema
    https://github.com/ClearURLs/Rules
    """

    def __init__(
        self,
        provider: str,
        url_pattern: str,
        rule_patterns: list[str] | None,
        raw_rule_patterns: list[str] | None,
        referral_marketing_patterns: list[str] | None,
        redirection_patterns: list[str] | None,
        exception_patterns: list[str] | None,
    ):
        """
        Ingests a provider object, builds regex rules
        """
        self.provider = provider
        self.url_pattern = re.compile(url_pattern)
        self.rules = [
            re.compile(rule)
            for rule in set(
                (rule_patterns or [])
                + (raw_rule_patterns or [])
                + (referral_marketing_patterns or [])
            )
        ]
        self.redirections = [
            re.compile(pattern) for pattern in redirection_patterns or []
        ]
        self.exceptions = [re.compile(pattern) for pattern in exception_patterns or []]

    def matches(self, url: str) -> bool:
        """
        Determines if a URL matches this provider's URL pattern,
        and does not match any of its exception patterns
        """
        url = url.strip()
        return bool(self.url_pattern.match(url)) and not any(
            exc.match(url) for exc in self.exceptions
        )

    def strip_params(self, url: str) -> str:
        """
        Strips tracking parameters per this provider's rules
        """
        parsed = urllib.parse.urlparse(url)

        params = urllib.parse.parse_qs(parsed.query)
        filtered_params = [
            (key, value)
            for key, value in params.items()
            if not any(rule.match(key) for rule in self.rules)
        ]

        new_query = urllib.parse.urlencode(filtered_params, doseq=True)
        parsed_writeable = parsed._asdict()
        parsed_writeable["query"] = new_query

        return cast(str, urllib.parse.urlunparse(parsed_writeable.values()))

    def redirect(self, url: str) -> str:
        """
        Performs a simulated redirect per this provider's redirection patterns.
        This prevents tracking across site redirects.

        Eagerly returns the transformation described by the pattern for the first
        pattern in this provider's ``self.redirections`` which matches the URL.
        """
        for redirect in self.redirections:
            if match := redirect.match(url):
                # If the URI is encoded as part of the redirect,
                # we need to decode it to be a valid URL
                new_url = _decode_uri(match.group(1))

                # If the redirection URI does not have a scheme,
                # we borrow the scheme from its parent URL
                if not util.URL_REGEX.match(new_url):
                    original_scheme = urllib.parse.urlparse(url).scheme
                    scheme = f"{original_scheme}://"
                else:
                    scheme = ""

                return f"{scheme}{new_url}"

        return url

    def clean(self, url: str) -> str:
        """
        Strips the URL completely of any tracking data per the rules defined by
        this provider
        """
        stripped = self.strip_params(url)
        redirected = self.redirect(stripped)

        return redirected

    def __repr__(self) -> str:
        return self.provider


rules_checksum: str = ""
rules_last_download: datetime = datetime.fromtimestamp(0.0, tz=UTC)
providers: list[ClearURLsProvider] = []


def _compute_rules_checksum(rules: str) -> str:
    return hashlib.sha256(rules.encode()).hexdigest()


def _download_new_rules(rules_url: str) -> str:
    """
    Downloads the rules file from the configured URL, updates the checksum and the
    last download timestamp if the data is new

    If there is no new data, just returns an empty string
    """
    log.info("Downloading ClearURLs rules...")
    with urllib.request.urlopen(rules_url) as manifest:
        data = cast(str, manifest.read().strip().decode())

    if not data:
        log.warning("Did not resolve any data from ClearURLs")
        return ""

    global rules_last_download
    global rules_checksum
    rules_last_download = datetime.now(UTC)
    new_checksum = _compute_rules_checksum(data)
    if new_checksum != rules_checksum:
        rules_checksum = new_checksum
        return data

    return ""


class _ProviderSchema(pydantic.BaseModel):
    class Config:
        extra = "ignore"

    urlPattern: str
    rules: list[str] | None = None
    rawRules: list[str] | None = None
    referralMarketing: list[str] | None = None
    redirections: list[str] | None = None
    exceptions: list[str] | None = None


def _json_to_provider(
    provider: str, provider_data: dict[str, str | list[str]]
) -> ClearURLsProvider | None:
    """
    Maps raw provider JSON data to a ``ClearURLsProvider`` object.
    Validates the ``provider_data`` before converting.
    """

    try:
        validated_data = _ProviderSchema(**provider_data)  # type: ignore[arg-type]
    except pydantic.ValidationError as e:
        log.exception(f"ClearURLs provider {provider} failed validation", exc_info=e)
        return None

    return ClearURLsProvider(
        provider,
        validated_data.urlPattern,
        validated_data.rules,
        validated_data.rawRules,
        validated_data.referralMarketing,
        validated_data.redirections,
        validated_data.exceptions,
    )


def _convert_rules_to_providers(rules: str) -> list[ClearURLsProvider]:
    """
    Converts the raw block of JSON rules into a list of ``ClearURLsProvider`` objects.

    Creates one ``ClearURLsProvider`` for each key under the top-level "providers" entry
    in the provided JSON.
    """
    log.info("Resolving ClearURLs providers...")
    try:
        all_providers = json.loads(rules).get("providers")
    except json.JSONDecodeError as e:
        raise exception.MemebotInternalError(
            f"Malformed ClearURLs manifest: {rules}"
        ) from e

    if not all_providers:
        raise exception.MemebotInternalError(f"Malformed ClearURLs manifest: {rules}")

    resolved_providers = []
    all_providers |= _CUSTOM_PROVIDERS
    for name in all_providers:
        provider_data = all_providers[name]
        new_provider = _json_to_provider(name, provider_data)

        if new_provider:
            resolved_providers.append(new_provider)

    log.info("Done.")
    return resolved_providers


def _refresh_providers() -> None:
    global providers
    new_rules = None
    try:
        new_rules = _download_new_rules(config.clearurls_rules_url)
    except exception.MemebotInternalError as e:
        # If we don't have any providers from a previous run,
        # we can't proceed further
        if not providers:
            raise e
        log.warning(f"Failed to download new ClearURLs rules: {e}")

    if new_rules:
        new_providers = _convert_rules_to_providers(new_rules)
        if new_providers:
            providers = new_providers


def strip_trackers(dirty_url: str) -> str:
    """
    Cleans a URL of all tracking metadata. Cleans tracking parameters and performs
    redirects in-place to prevent sharing traffic with affiliates.
    """
    dirty_url = dirty_url.strip()
    global providers
    if rules_last_download + config.clearurls_rules_refresh_hours < datetime.now(UTC):
        _refresh_providers()

    if not providers:
        raise exception.MemebotInternalError(
            f"Failed to strip tracking params from {dirty_url}: No ClearURLs providers"
        )

    # Repeatedly clean the URL with all providers whose patterns match it
    return functools.reduce(
        lambda url, provider: provider.clean(url),
        (provider for provider in providers if provider.matches(dirty_url)),
        dirty_url,
    )
