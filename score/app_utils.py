import logging
from typing import Any
from urllib.parse import quote_plus
from .models import Source, Package, Vulnerabilities
from .pypi.json_scraper import get_package_data as get_pypi_package_data
from .conda.scrape_conda import get_conda_package_data
from .npm.scrape_npm import get_npm_package_data
from .git_vcs.scrape import create_git_metadata_str
from .vulnerabilities.scrape_vulnerabilities import scrape_vulnerability
from .utils.caching import save_to_cache, cache_hit, load_from_cache, cache_path

max_age = 60 * 60
log = logging.getLogger(__name__)


def create_git_metadata_cached(url: str, extra_headers: Any) -> Source:

    cache_filename = cache_path(f"/git/{quote_plus(url)}.json")
    extra_headers["git-cache-file"] = cache_filename

    if cache_hit(cache_filename, days=1):
        cached_git = load_from_cache(Source, cache_filename)
        if cached_git is not None:
            extra_headers["git-cache-hit"] = "true"
            return cached_git

    extra_headers["git-cache-hit"] = "false"
    git = create_git_metadata_str(url)

    save_to_cache(git, cache_filename)

    return git


def get_vuln_data_cached(
    ecosystem: str, package_name: str, extra_headers: Any
) -> Vulnerabilities:
    cache_filename = cache_path(f"vuln/{ecosystem}/{package_name}.json")
    extra_headers["vuln-cache-file"] = cache_filename

    if cache_hit(cache_filename, days=7):
        cached_vuln = load_from_cache(Vulnerabilities, cache_filename)
        if cached_vuln is not None:
            extra_headers["vuln-cache-hit"] = "true"
            return cached_vuln

    log.info(f"Cache miss for {ecosystem}/{package_name}")
    extra_headers["vuln-cache-hit"] = "false"
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

    raise ValueError(f"Unsupported ecosystem: {ecosystem}")


def get_package_data_cached(
    ecosystem: str, package_name: str, extra_headers: Any
) -> Package:

    cache_filename = cache_path(f"packages/{ecosystem}/{package_name}.json")
    extra_headers["pkg-cache-file"] = cache_filename

    if cache_hit(cache_filename, days=1):
        cached_pkg = load_from_cache(Package, cache_filename)
        if cached_pkg is not None:
            extra_headers["pkg-cache-hit"] = "true"
            return cached_pkg

    log.info(f"Cache miss for {ecosystem}/{package_name}")
    extra_headers["pkg-cache-hit"] = "false"
    pkg = get_package_data(ecosystem, package_name)

    save_to_cache(pkg, cache_filename)

    return pkg
