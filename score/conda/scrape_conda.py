from dateutil.parser import parse as parsedate
from ..utils.request_session import get_session

CONDA_PACKAGE_URL_TEMPLATE = "https://api.anaconda.org/package/{channel}/{package}"


def get_conda_package_data(channel, package_name: str):
    s = get_session()
    url = CONDA_PACKAGE_URL_TEMPLATE.format(channel=channel, package=package_name)
    res = s.get(url)
    res.raise_for_status()
    package_data = res.json()

    ndownloads = 0
    for f in package_data["files"]:
        ndownloads += f["ndownloads"]
    source_url = package_data.get("dev_url") or package_data.get("source_git_url")
    return {
        "name": package_data["name"],
        "full_name": package_data["full_name"],
        "source_url": source_url,
        "latest_version": package_data["latest_version"],
        "ndownloads": ndownloads,
        "release_date": parsedate(package_data["modified_at"]),
    }
