import os
from fastapi import FastAPI

from .app_utils import (
    get_conda_package_data_cached,
    get_pypi_package_data_cached,
    create_git_metadata_cached,
    convert_numpy_types,
)


app = FastAPI()


@app.get("/")
async def root():
    return {"version": os.environ.get("K_REVISION", "?")}


@app.get("/pypi/{package_name}")
def pypi(package_name):
    data = get_pypi_package_data_cached(package_name)
    return {"ecosystem": "pypi", "package_name": package_name, "data": data}


@app.get("/conda/{channel}/{package_name}")
def conda(channel, package_name):
    data = get_conda_package_data_cached(channel, package_name)
    return {
        "ecosystem": "conda",
        "channel": channel,
        "package_name": package_name,
        "data": data,
    }


@app.get("/git/{source_url:path}")
def git(source_url):
    data = create_git_metadata_cached(source_url)
    data = convert_numpy_types(data)
    return {"source_url": source_url, "data": data}
