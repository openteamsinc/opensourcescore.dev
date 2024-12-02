import numpy as np
from typing import Any
from fastapi import FastAPI
from .pypi.json_scraper import get_package_data
from .conda.scrape_conda import get_conda_package_data
from .git_vcs.scrape import create_git_metadata

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/pypi/{package_name}")
async def pypi(package_name):
    data = get_package_data(package_name)
    return {"ecosystem": "pypi", "package_name": package_name, "data": data}


@app.get("/conda/{channel}/{package_name}")
async def conda(channel, package_name):
    data = get_conda_package_data(channel, package_name)
    return {
        "ecosystem": "conda",
        "channel": channel,
        "package_name": package_name,
        "data": data,
    }


def convert_numpy_types(obj: Any) -> Any:
    # Handle numpy types
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()

    # Handle nested dictionaries
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}

    # Handle lists, tuples, and other iterables
    if isinstance(obj, (list, tuple, set)):
        return type(obj)(convert_numpy_types(item) for item in obj)

    return obj


@app.get("/git/{source_url:path}")
async def git(source_url):
    data = create_git_metadata(source_url)
    data = convert_numpy_types(data)
    return {"source_url": source_url, "data": data}
