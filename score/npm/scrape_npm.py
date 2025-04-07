import logging
from typing import Optional
from datetime import datetime

log = logging.getLogger(__name__)
from dateutil.parser import parse as parse_date
from score.models import Package
from ..utils.request_session import get_session
from ..utils.normalize_source_url import normalize_source_url

NPM_PACKAGE_TEMPLATE_URL = "https://registry.npmjs.org/{package_name}"


def try_parse_date(release_date: Optional[str]) -> Optional[datetime]:
    if release_date is None:
        return None

    try:
        return parse_date(release_date)
    except Exception as e:
        log.debug(f"Failed to parse date {release_date}: {e}")
        return None


def get_npm_package_data(package_name: str) -> Package:
    s = get_session()
    url = NPM_PACKAGE_TEMPLATE_URL.format(package_name=package_name)
    res = s.get(url)

    if res.status_code == 404:
        log.debug(f"Skipping package not found for package {package_name}")
        return Package(name=package_name, ecosystem="npm", status="not_found")
    res.raise_for_status()
    package_data = res.json()

    source_url = package_data.get("repository", {}).get("url")
    source_url = normalize_source_url(source_url)

    # ndownloads = get_npm_package_downloads(package)
    version = package_data.get("dist-tags", {}).get("latest")
    release_date = package_data.get("time", {}).get(version)
    license = package_data.get("license")

    return Package(
        name=package_name,
        version=version,
        source_url=source_url,
        release_date=try_parse_date(release_date),
        ecosystem="npm",
        license=license,
    )
