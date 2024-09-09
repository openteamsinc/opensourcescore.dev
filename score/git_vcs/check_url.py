from urllib.parse import urlparse
from typing import Tuple


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
            "error": "Source code location 'http://' does not use a secure connection",
        }

    if URL.hostname == "localhost":
        return False, {
            "source_url": url,
            "error": "Source code location is a localhost url",
        }
    if not is_valid_hostname(URL.hostname):
        return False, {
            "source_url": url,
            "error": "Source code location is not a valid url",
        }

    if URL.hostname.startswith("127."):  # type: ignore
        return False, {
            "source_url": url,
            "error": "Source code location is a localhost url",
        }

    return False, {
        "source_url": url,
        "error": "Source code location is not a valid url",
    }
