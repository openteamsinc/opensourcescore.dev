from urllib.parse import urlparse
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


def get_source_from_url(url: str) -> Source:
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
