import logging
from typing import Callable
from urllib.parse import quote_plus

from fastapi import HTTPException

from .conda.scrape_conda import get_conda_package_data
from .git_vcs.scrape import create_git_metadata
from .models import Package, Source, Vulnerabilities
from .npm.scrape_npm import get_npm_package_data
from .pypi.json_scraper import get_package_data as get_pypi_package_data
from .utils.caching import cache_hit, cache_path, load_from_cache, save_to_cache
from .vulnerabilities.scrape_vulnerabilities import scrape_vulnerability

max_age = 60 * 60
log = logging.getLogger(__name__)

AppendHeader = Callable[[str, str], None]


def create_git_metadata_cached(
    url: str, append_header: AppendHeader, invalidate_cache=False
) -> Source:

    cache_filename = cache_path(f"/git/{quote_plus(url)}.json")
    append_header("git-cache-file", cache_filename)

    if not invalidate_cache and cache_hit(cache_filename, days=1):
        cached_git = load_from_cache(Source, cache_filename)
        if cached_git is not None:
            append_header("git-cache-hit", "true")
            return cached_git

    append_header("git-cache-hit", "false")
    git = create_git_metadata(url)

    save_to_cache(git, cache_filename)

    return git


def get_vuln_data_cached(
    ecosystem: str,
    package_name: str,
    append_header: AppendHeader,
    invalidate_cache=False,
) -> Vulnerabilities:
    cache_filename = cache_path(f"vuln/{ecosystem}/{package_name}.json")
    append_header("vuln-cache-file", cache_filename)

    if not invalidate_cache and cache_hit(cache_filename, days=7):
        cached_vuln = load_from_cache(Vulnerabilities, cache_filename)
        if cached_vuln is not None:
            append_header("vuln-cache-hit", "true")
            return cached_vuln

    log.info(f"Cache miss for {ecosystem}/{package_name}")
    append_header("vuln-cache-hit", "false")
    vuln = scrape_vulnerability(ecosystem, package_name)

    save_to_cache(vuln, cache_filename)

    return vuln


def get_package_data(ecosystem: str, package_name: str) -> Package:
    if ecosystem == "pypi":
        return get_pypi_package_data(package_name)
    if ecosystem == "conda":
        return get_conda_package_data(package_name)
    if ecosystem == "npm":
        return get_npm_package_data(package_name)

    raise HTTPException(status_code=404, detail=f"Unsupported ecosystem: {ecosystem}")


def get_package_data_cached(
    ecosystem: str,
    package_name: str,
    append_header: AppendHeader,
    invalidate_cache=False,
) -> Package:

    cache_filename = cache_path(f"packages/{ecosystem}/{package_name}.json")
    append_header("pkg-cache-file", cache_filename)

    if not invalidate_cache and cache_hit(cache_filename, days=1):
        cached_pkg = load_from_cache(Package, cache_filename)
        if cached_pkg is not None:
            append_header("pkg-cache-hit", "true")

            log.info(
                f"Cache hit for {ecosystem}/{package_name}",
                extra={
                    "package_status": cached_pkg.status,
                    "ecosystem": ecosystem,
                    "package_name": package_name,
                },
            )

            return cached_pkg

    append_header("pkg-cache-hit", "false")
    pkg = get_package_data(ecosystem, package_name)

    log.info(
        f"Cache miss for {ecosystem}/{package_name}",
        extra={
            "package_status": pkg.status,
            "ecosystem": ecosystem,
            "package_name": package_name,
        },
    )

    save_to_cache(pkg, cache_filename)

    return pkg
