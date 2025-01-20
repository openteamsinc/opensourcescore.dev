from urllib.parse import urlparse


def normalize_source_url(url: str):
    URL = urlparse(url)
    if URL.hostname in ["github.com", "gitlab.com", "bitbucket.org"]:
        path_components = URL.path.strip("/").split("/")
        if len(path_components) != 2:
            # Invalid git*.com/ URL
            return None
        org, repo = path_components
        if repo.endswith(".git"):
            repo = repo[:-4]

        return f"https://{URL.hostname}/{org}/{repo}"

    return url
