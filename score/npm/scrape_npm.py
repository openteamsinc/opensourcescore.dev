import logging

log = logging.getLogger(__name__)

from ..utils.request_session import get_session
from ..utils.normalize_source_url import normalize_source_url

NPM_PACKAGE_TEMPLATE_URL = "https://registry.npmjs.org/{package_name}"


def get_npm_package_data(package_name):
    s = get_session()
    url = NPM_PACKAGE_TEMPLATE_URL.format(package_name=package_name)
    res = s.get(url)

    if res.status_code == 404:
        log.debug(f"Skipping package not found for package {package_name}")
        return {"status": "not_found"}
    res.raise_for_status()
    package_data = res.json()

    source_url = package_data.get("repository", {}).get("url")
    source_url = normalize_source_url(source_url)

    # ndownloads = get_npm_package_downloads(package)
    version = package_data.get("dist-tags", {}).get("latest")
    release_date = package_data.get("time", {}).get(version)
    return {
        "name": package_name,
        "version": version,
        "source_url": source_url,
        "release_date": release_date,
    }
