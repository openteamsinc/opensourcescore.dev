from dateutil.parser import parse as parsedate
from fastapi import HTTPException

from score.models import Package, Dependency

from ..utils.request_session import get_session

CONDA_PACKAGE_URL_TEMPLATE = "https://api.anaconda.org/package/{channel}/{package}"


def get_conda_package_data(channel_package_name: str) -> Package:

    if "/" not in channel_package_name:
        raise HTTPException(
            status_code=404,
            detail=(
                "Invalid conda package name. Expected format: "
                f"<channel>/<package_name> (got {channel_package_name})"
            ),
        )
    channel, package_name = channel_package_name.split("/", 1)

    s = get_session()
    url = CONDA_PACKAGE_URL_TEMPLATE.format(channel=channel, package=package_name)
    res = s.get(url)
    if res.status_code == 404:
        return Package(
            name=channel_package_name,
            ecosystem="conda",
            status="not_found",
            dependencies=[],
        )
    res.raise_for_status()

    package_data = res.json()

    ndownloads = 0
    for f in package_data["files"]:
        ndownloads += f["ndownloads"]
    source_url = package_data.get("dev_url") or package_data.get("source_git_url")
    version = package_data["latest_version"]

    depstrings = {
        depstr.split(" ", 1)[0]: depstr.split(" ", 1)[1]
        for fdata in package_data["files"]
        if fdata["version"] == version
        for depstr in fdata["attrs"]["depends"]
    }
    dependencies = [
        Dependency(name=f"{channel}/{name}", specifiers=spec)
        for name, spec in depstrings.items()
    ]

    return Package(
        name=package_data["full_name"],
        ecosystem="conda",
        dependencies=dependencies,
        source_url=source_url,
        version=version,
        release_date=parsedate(package_data["modified_at"]),
    )
