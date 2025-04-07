from urllib.parse import urlparse
from typing import Tuple
from score.notes import Note
from score.models import Source


def is_valid_hostname(hostname):
    if not hostname:
        return False
    if 3 > len(hostname) > 255:
        return False
    if "." not in hostname:
        return False
    if ":" in hostname:
        return False
    return True


def check_url(url: str) -> Tuple[bool, dict]:
    URL = urlparse(url)

    if URL.scheme in ["https", "git"]:
        return True, {"source_url": url}

    if URL.scheme == "http":
        return False, {
            "source_url": url,
            "error": Note.NO_SOURCE_INSECURE_CONNECTION,
        }

    if URL.hostname == "localhost":
        return False, {
            "source_url": url,
            "error": Note.NO_SOURCE_LOCALHOST_URL,
        }
    if not is_valid_hostname(URL.hostname):
        return False, {
            "source_url": url,
            "error": Note.NO_SOURCE_INVALID_URL,
        }

    if URL.hostname.startswith("127."):  # type: ignore
        return False, {
            "source_url": url,
            "error": Note.NO_SOURCE_LOCALHOST_URL,
        }

    return False, {
        "source_url": url,
        "error": Note.NO_SOURCE_INVALID_URL,
    }


def check_url_str(url: str) -> Source:
    URL = urlparse(url)

    if URL.scheme in ["https", "git"]:
        return Source(source_url=url)

    if URL.scheme == "http":
        return Source(
            source_url=url,
            error=Note.NO_SOURCE_INSECURE_CONNECTION,
        )

    if URL.hostname == "localhost":
        return Source(
            source_url=url,
            error=Note.NO_SOURCE_LOCALHOST_URL,
        )

    if not is_valid_hostname(URL.hostname):
        return Source(
            source_url=url,
            error=Note.NO_SOURCE_INVALID_URL,
        )

    if URL.hostname.startswith("127."):  # type: ignore
        return Source(
            source_url=url,
            error=Note.NO_SOURCE_LOCALHOST_URL,
        )

    return Source(
        source_url=url,
        error=Note.NO_SOURCE_INVALID_URL,
    )
