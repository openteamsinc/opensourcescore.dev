import logging
from typing import Dict, List, Optional, Tuple

from dateutil.parser import parse as parsedate

from score.models import Package

from ..utils.common_license_names import get_kind_from_common_license_name
from ..utils.normalize_source_url import normalize_source_url
from ..utils.request_session import get_session
from .parse_deps import parse_deps

log = logging.getLogger(__name__)


def get_license_from_classifier(classifier: str) -> Optional[str]:

    [first, *rest] = classifier.split(" :: ")
    if first.lower() != "license":
        return None
    if len(rest) == 0:
        return None
    if len(rest) == 1:
        return rest[0]

    if rest[0] == "OSI Approved":
        oss = " :: ".join(rest[1:])
        return oss

    return " :: ".join(rest[1:])


def get_license_from_classifiers(classifiers: List[str]) -> Optional[str]:
    for classifier in classifiers:
        license = get_license_from_classifier(classifier)
        if license:
            return license
    return None


def get_package_data(package_name: str) -> Package:
    """
    Fetches package data from the PyPI JSON API for a given package name and filters out specific fields.
    Additionally fetches download counts from the PyPI Stats API.

    Args:
        package_name (str): The name of the package to fetch data for.

    Returns:
        dict: A dictionary containing filtered package data.
    """
    s = get_session()
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = s.get(url)
    if response.status_code == 404:
        log.debug(f"Skipping package not found for package {package_name}")
        return Package(
            name=package_name,
            ecosystem="pypi",
            status="not_found",
            dependencies=[],
        )
    response.raise_for_status()  # Raise an error for bad status codes
    package_data = response.json()  # Parse the JSON response

    # Extract the 'info' section
    info = package_data.get("info", {})

    dependencies = parse_deps(info.get("requires_dist"))
    source_url_key, source_url = extract_source_url(info.get("project_urls", {}))

    version = info.get("version", None)
    release_date = None
    release_info = package_data.get("releases", {}).get(version, [])

    if version and release_info:
        upload_dates = [
            parsedate(i.get("upload_time"))
            for i in release_info
            if i.get("upload_time")
        ]
        first_upload_date = min(upload_dates)
        release_date = first_upload_date

    license = info.get("license")
    if not license:
        license = get_license_from_classifiers(info.get("classifiers", []))
    license = get_kind_from_common_license_name(license)

    package_data = Package(
        name=package_name,
        dependencies=dependencies,
        version=version,
        source_url=source_url,
        source_url_key=source_url_key,
        release_date=release_date,
        license=license,
        ecosystem="pypi",
    )
    return package_data


def extract_source_url(
    project_urls: Dict[str, str],
) -> Tuple[Optional[str], Optional[str]]:
    if not project_urls:
        return None, None

    project_urls = {k.lower(): v for k, v in project_urls.items()}

    for key in ["code", "repository", "source", "source code", "github", "homepage"]:
        if key not in project_urls:
            continue
        source_url = normalize_source_url(project_urls[key])
        if source_url:
            return key, source_url

    return None, None
