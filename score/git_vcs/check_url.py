from urllib.parse import urlparse
from typing import Tuple
from ..notes import Note


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
            "error": Note.INSECURE_CONNECTION.value,
        }

    if URL.hostname == "localhost":
        return False, {
            "source_url": url,
            "error": Note.LOCALHOST_URL.value,
        }
    if not is_valid_hostname(URL.hostname):
        return False, {
            "source_url": url,
            "error": Note.INVALID_URL.value,
        }

    if URL.hostname.startswith("127."):  # type: ignore
        return False, {
            "source_url": url,
            "error": Note.LOCALHOST_URL.value,
        }

    return False, {
        "source_url": url,
        "error": Note.INVALID_URL.value,
    }


def check_url_str(url: str) -> Tuple[bool, dict]:
    URL = urlparse(url)

    if URL.scheme in ["https", "git"]:
        return True, {"source_url": url}

    if URL.scheme == "http":
        return False, {
            "source_url": url,
            "error": Note.INSECURE_CONNECTION.name,
        }

    if URL.hostname == "localhost":
        return False, {
            "source_url": url,
            "error": Note.LOCALHOST_URL.name,
        }
    if not is_valid_hostname(URL.hostname):
        return False, {
            "source_url": url,
            "error": Note.INVALID_URL.name,
        }

    if URL.hostname.startswith("127."):  # type: ignore
        return False, {
            "source_url": url,
            "error": Note.LOCALHOST_URL.name,
        }

    return False, {
        "source_url": url,
        "error": Note.INVALID_URL.name,
    }
