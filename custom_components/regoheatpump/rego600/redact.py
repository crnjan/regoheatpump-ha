"""Helpers for hiding secrets in connection URLs."""

import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

_SECRET_PARAMS = frozenset({"key", "noise_psk", "password"})
_MASK = "***"

# A URL inside free text, e.g. "Rego Heat Pump (Rego 637, esphome://…)".
# Stops at whitespace and ")" so surrounding text is kept.
_EMBEDDED_URL = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*://[^\s)]+")


def redact_url(url: str) -> str:
    """Return the URL with credentials and secret query values masked.

    Used for anything user-visible (entry titles, logs). Paths such as
    ``/dev/ttyUSB0`` are returned unchanged.
    """
    if "://" not in url:
        return url

    parts = urlsplit(url)

    netloc = parts.netloc
    userinfo, sep, hostport = netloc.rpartition("@")
    if sep:
        user, colon, _ = userinfo.partition(":")
        netloc = f"{user}{colon}{_MASK if colon else ''}@{hostport}"

    query = parts.query
    if query:
        params = parse_qsl(query, keep_blank_values=True)
        if any(name in _SECRET_PARAMS for name, _ in params):
            query = urlencode(
                [
                    (name, _MASK if name in _SECRET_PARAMS else value)
                    for name, value in params
                ],
                safe="*",
            )

    return urlunsplit((parts.scheme, netloc, parts.path, query, parts.fragment))


def redact_urls_in_text(text: str) -> str:
    """Return the text with every embedded URL redacted."""
    return _EMBEDDED_URL.sub(lambda match: redact_url(match.group()), text)
