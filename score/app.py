import os
from typing import Optional
from fastapi import FastAPI, Request
from .score.app_score import build_score
from .notes import SCORE_ORDER, GROUPS, to_dict
from .app_utils import (
    get_conda_package_data_cached,
    get_pypi_package_data_cached,
    get_npm_package_data_cached,
    create_git_metadata_cached,
    convert_numpy_types,
    max_age,
)

app = FastAPI()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-control"] = f"max-age={max_age}, public"
    return response


@app.get("/")
async def root():
    return {"version": os.environ.get("K_REVISION", "?")}


@app.get("/notes")
async def notes():
    return to_dict()


@app.get("/notes/categories")
async def category_notes():
    return {
        "notes": {v["code"]: v for k, v in to_dict().items()},
        "categories": list(SCORE_ORDER),
        "groups": GROUPS,
    }


@app.get("/pkg/pypi/{package_name}")
def pypi(package_name):
    data = get_pypi_package_data_cached(package_name)

    return {"ecosystem": "pypi", "package_name": package_name, "data": data}


@app.get("/score/pypi/{package_name}")
def pypi_score(package_name, source_url: Optional[str] = None):
    package_data = get_pypi_package_data_cached(package_name)

    if not source_url:
        source_url = package_data.get("source_url")
    source_data = None
    if source_url:
        source_data = create_git_metadata_cached(source_url)
        source_data = convert_numpy_types(source_data)

    score = build_score(source_url, source_data, package_data)
    return {
        "ecosystem": "pypi",
        "package_name": package_name,
        "package": package_data,
        "source": source_data,
        "score": score,
        "status": package_data.get("status", "ok"),
    }


@app.get("/pkg/npm/{package_name}")
def npm(package_name):
    data = get_npm_package_data_cached(package_name)

    return {"ecosystem": "pypi", "package_name": package_name, "data": data}


@app.get("/score/npm/{package_name}")
def npm_score(package_name, source_url: Optional[str] = None):
    package_data = get_npm_package_data_cached(package_name)

    if not source_url:
        source_url = package_data.get("source_url")
    source_data = None
    if source_url:
        source_data = create_git_metadata_cached(source_url)
        source_data = convert_numpy_types(source_data)

    score = build_score(source_url, source_data, package_data)
    return {
        "ecosystem": "npm",
        "package_name": package_name,
        "package": package_data,
        "source": source_data,
        "score": score,
        "status": package_data.get("status", "ok"),
    }


@app.get("/pkg/conda/{channel}/{package_name}")
def conda(channel, package_name):
    data = get_conda_package_data_cached(channel, package_name)
    return {
        "ecosystem": "conda",
        "channel": channel,
        "package_name": package_name,
        "data": data,
    }


@app.get("/score/conda/{channel}/{package_name}")
def conda_score(channel, package_name, source_url: Optional[str] = None):
    package_data = get_conda_package_data_cached(channel, package_name)

    if not source_url:
        source_url = package_data.get("source_url")
    source_data = None
    if source_url:
        source_data = create_git_metadata_cached(source_url)
        source_data = convert_numpy_types(source_data)

    score = build_score(source_url, source_data, package_data)
    return {
        "ecosystem": "conda",
        "package_name": package_name,
        "package": package_data,
        "source": source_data,
        "score": score,
        "status": package_data.get("status", "ok"),
    }


@app.get("/source/git/{source_url:path}")
def git(source_url):
    data = create_git_metadata_cached(source_url)
    data = convert_numpy_types(data)
    return {"source_url": source_url, "data": data}


@app.get("/score/{ecosystem}/{package_name:path}", status_code=404)
def invalid_ecosystem(ecosystem):
    return {
        "detail": f"Ecosystem {ecosystem} not supported",
        "error": "invalid_ecosystem",
    }
