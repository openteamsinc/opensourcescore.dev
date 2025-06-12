import re
from urllib.parse import urlparse

TWO_COMPONENT_HOSTS = ["github.com", "gitlab.com", "bitbucket.org"]


def normalize_source_url(url: str | None):
    if not url:
        return None

    # replace git ssh syntax with url syntax
    url = re.sub(r"git@([^:]+):(.+)", r"https://\1/\2", url)

    URL = urlparse(url)
    if URL.hostname in TWO_COMPONENT_HOSTS:
        path_components = URL.path.strip("/").split("/")
        if len(path_components) != 2:
            # Invalid git*.com/ URL
            return None
        org, repo = path_components
        if repo.endswith(".git"):
            repo = repo[:-4]

        return f"https://{URL.hostname}/{org}/{repo}"

    return url
