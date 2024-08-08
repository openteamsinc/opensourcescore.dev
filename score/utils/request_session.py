import requests

from requests.adapters import HTTPAdapter, Retry


def get_session(retries=5, backoff_factor=0.1) -> requests.Session:

    s = requests.Session()

    retries = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[500, 502, 503, 504],
    )

    s.mount("https://", HTTPAdapter(max_retries=retries))
    return s
