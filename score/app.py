import os
import logging
from dataclasses import dataclass
from typing import Optional
from fastapi import FastAPI, Request, Response
from score.models import Package, Source, Score, NoteDescr, Vulnerabilities
from .score.app_score import build_score
from .notes import SCORE_ORDER, GROUPS, to_dict
from .app_utils import (
    get_package_data_cached,
    get_vuln_data_cached,
    create_git_metadata_cached,
    max_age,
)


logging.basicConfig(level=logging.INFO)

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
    vulnerabilities: Vulnerabilities


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)

    response.headers["Cache-control"] = f"max-age={max_age}, public"
    response.headers["Content-Language"] = "en-US"
    response.headers["App"] = f"{TITLE} {VERSION}".encode(
        "ascii", errors="ignore"
    ).decode(errors="ignore")
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


@app.get("/pkg/{ecosystem}/{package_name:path}", tags=["pkg"], response_model=Package)
def get_pkg(response: Response, ecosystem: str, package_name: str):

    data = get_package_data_cached(ecosystem, package_name, response.headers.append)

    return data


@app.get(
    "/score/{ecosystem}/{package_name:path}",
    tags=["score"],
    summary="get the score for a package",
    response_model=ScoreResponse,
)
def any_score(
    response: Response,
    ecosystem: str,
    package_name: str,
    source_url: Optional[str] = None,
):

    package_data = get_package_data_cached(
        ecosystem, package_name, response.headers.append
    )

    if not source_url:
        source_url = package_data.source_url
    source_data = None
    if source_url:
        source_data = create_git_metadata_cached(source_url, response.headers.append)

    vuln_data = get_vuln_data_cached(ecosystem, package_name, response.headers.append)

    score = build_score(source_url, source_data, package_data, vuln_data)

    return ScoreResponse(
        ecosystem=ecosystem,
        package_name=package_name,
        package=package_data,
        source=source_data,
        score=score,
        status=package_data.status,
        vulnerabilities=vuln_data,
    )


@app.get("/source/git/{source_url:path}", tags=["source", "git"], response_model=Source)
def git(response: Response, source_url: str):
    data = create_git_metadata_cached(source_url, response.headers.append)
    return data
