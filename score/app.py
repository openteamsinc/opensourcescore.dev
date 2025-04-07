import os
from dataclasses import dataclass
from typing import Optional
from fastapi import FastAPI, Request
from score.models import Package, Source, Score, NoteDescr
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

TITLE = "opensourcescore.dev"
VERSION = os.environ.get("K_REVISION", "¿dev?")
COMMIT = VERSION.rsplit("-", 1)[-1]
DEPLOY_DATE = os.environ.get("DEPLOY_DATE", "¿today?")
SOURCE_URL = f"https://github.com/openteamsinc/opensourcescore.dev/commit/{COMMIT}"
DESCRIPTION = f"""

Info:
 * Last deployed: {DEPLOY_DATE}
 * Github repo: [github.com/openteamsinc/opensourcescore.dev](https://github.com/openteamsinc/opensourcescore.dev)
 * Commit: [{COMMIT}]({SOURCE_URL})

    """

app = FastAPI(
    title="opensourcescore.dev",
    summary="Discover and evaluate open source projects with ease",
    description=DESCRIPTION,
    version=VERSION,
)


@dataclass
class NotesResponse:
    notes: dict[str, NoteDescr]
    categories: list[str]
    groups: dict[str, list[str]]


@dataclass
class ScoreResponse:
    ecosystem: str
    package_name: str
    package: Package
    source: Optional[Source]
    score: Score
    status: str


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-control"] = f"max-age={max_age}, public"
    response.headers["Content-Language"] = "en-US"
    response.headers["App"] = f"{TITLE} {VERSION}"
    return response


@app.get("/")
async def root():

    return {
        "version": VERSION,
        "html_docs_url": "https://opensourcescore.dev/docs",
        "source_code_url": f"https://github.com/openteamsinc/opensourcescore.dev/commit/{COMMIT}",
    }


@app.get("/notes", tags=["notes"], summary="depricated")
async def notes():
    "depricated"
    return to_dict()


@app.get(
    "/notes/categories",
    tags=["notes"],
    summary="Return notes in a dictionary format",
    response_model=NotesResponse,
)
async def category_notes():
    return {
        "notes": {v["code"]: v for k, v in to_dict().items()},
        "categories": list(SCORE_ORDER),
        "groups": GROUPS,
    }


@app.get("/pkg/pypi/{package_name}", tags=["pkg", "pypi"])
def pypi(package_name):
    data = get_pypi_package_data_cached(package_name)

    return {"ecosystem": "pypi", "package_name": package_name, "data": data}


@app.get(
    "/score/pypi/{package_name}",
    tags=["score", "pypi"],
    summary="get the score for a pypi package",
    response_model=ScoreResponse,
)
def pypi_score(package_name, source_url: Optional[str] = None):
    package_data = get_pypi_package_data_cached(package_name)

    if not source_url:
        source_url = package_data.source_url
    source_data = None
    if source_url:
        source_data = create_git_metadata_cached(source_url)
        source_data = convert_numpy_types(source_data)

    score = build_score(source_url, source_data, package_data)
    return ScoreResponse(
        ecosystem="pypi",
        package_name=package_name,
        package=package_data,
        source=source_data,
        score=score,
        status=package_data.status,
    )


@app.get("/pkg/npm/{package_name}", tags=["pkg", "npm"])
def npm(package_name):
    data = get_npm_package_data_cached(package_name)

    return {"ecosystem": "pypi", "package_name": package_name, "data": data}


@app.get(
    "/score/npm/{package_name}",
    tags=["score", "npm"],
    summary="get the score for an npm package",
    response_model=ScoreResponse,
)
def npm_score(package_name, source_url: Optional[str] = None):
    package_data = get_npm_package_data_cached(package_name)

    if not source_url:
        source_url = package_data.source_url
    source_data = None
    if source_url:
        source_data = create_git_metadata_cached(source_url)
        source_data = convert_numpy_types(source_data)

    score = build_score(source_url, source_data, package_data)
    return ScoreResponse(
        ecosystem="npm",
        package_name=package_name,
        package=package_data,
        source=source_data,
        score=score,
        status=package_data.status,
    )


@app.get("/pkg/conda/{channel}/{package_name}", tags=["pkg", "conda"])
def conda(channel, package_name):
    data = get_conda_package_data_cached(channel, package_name)
    return {
        "ecosystem": "conda",
        "channel": channel,
        "package_name": package_name,
        "data": data,
    }


@app.get(
    "/score/conda/{channel}/{package_name}",
    tags=["score", "conda"],
    summary="get the score for a conda package",
)
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


@app.get("/source/git/{source_url:path}", tags=["source", "git"])
def git(source_url):
    data = create_git_metadata_cached(source_url)
    data = convert_numpy_types(data)
    return {"source_url": source_url, "data": data}


@app.get(
    "/score/{ecosystem}/{package_name:path}",
    status_code=404,
    tags=["score", "errors"],
    summary="Return 404 error for unsupported ecosystem",
)
def invalid_ecosystem(ecosystem):
    return {
        "detail": f"Ecosystem {ecosystem} not supported",
        "error": "invalid_ecosystem",
    }
