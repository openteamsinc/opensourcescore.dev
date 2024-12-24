import os
from fastapi import FastAPI, Request
from datetime import timedelta
from .app_utils import (
    get_conda_package_data_cached,
    get_pypi_package_data_cached,
    get_npm_package_data_cached,
    create_git_metadata_cached,
    convert_numpy_types,
    max_age,
)
from .score.score import safe_date_diff
from .score.maturity import build_maturity_score
from .score.health_risk import (
    build_health_risk_score,
    Score,
    CAUTION_NEEDED,
    HIGH_RISK,
    MODERATE_RISK,
)
from .notes import Note

app = FastAPI()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-control"] = f"max-age={max_age}, public"
    return response


@app.get("/")
async def root():
    return {"version": os.environ.get("K_REVISION", "?")}


@app.get("/pypi/{package_name}")
def pypi(package_name):
    data = get_pypi_package_data_cached(package_name)

    return {"ecosystem": "pypi", "package_name": package_name, "data": data}


def score_python(package_data: dict, source_data: dict, score: Score):

    if not package_data:
        return

    expected_name = source_data.get("py_package")
    actual_name = package_data.get("name")

    if not expected_name:
        score.limit(CAUTION_NEEDED)
        score.notes.append(Note.NO_PROJECT_NAME.value)
        return

    if expected_name != actual_name:
        score.limit(HIGH_RISK)
        score.notes.append(Note.PACKAGE_NAME_MISMATCH.value)

    one_year = timedelta(days=365)
    skew = safe_date_diff(
        source_data.get("latest_commit"), package_data.get("release_date")
    )
    if skew and skew > one_year:
        score.limit(MODERATE_RISK)
        score.notes.append(Note.PACKGE_SKEW_NOT_UPDATED.value)

    if skew and skew < -one_year:
        score.limit(MODERATE_RISK)
        score.notes.append(Note.PACKGE_SKEW_NOT_RELEASED.value)

    return


def build_score(source_url, source_data, package_data):
    score: dict = {
        "source_url": source_url,
        "packages": [],
        "ecosystem_destination": {
            "pypi": source_data.get("py_package"),
            "npm": None,
            "conda": None,
        },
    }

    score["maturity"] = build_maturity_score(source_url, source_data)
    sc = build_health_risk_score(source_data)
    score_python(package_data, source_data, sc)
    score["health_risk"] = sc.dict_string_notes()
    score["last_updated"] = source_data["latest_commit"]

    license = source_data.get("license")
    if license:
        score["license"] = license["license"]
        score["license_kind"] = license["kind"]
        score["license_modified"] = license["modified"]

    return score


@app.get("/pypi/{package_name}/score")
def pypi_score(package_name):
    package_data = get_pypi_package_data_cached(package_name)

    source_url = package_data.get("source_url")
    source_data = None
    print("package_data", package_data)
    if source_url:
        print("fetch source")
        source_data = create_git_metadata_cached(source_url)
        source_data = convert_numpy_types(source_data)

    score = build_score(source_url, source_data, package_data)
    return {
        "ecosystem": "pypi",
        "package_name": package_name,
        "package": package_data,
        "source": source_data,
        "score": score,
    }


@app.get("/npm/{package_name}")
def npm(package_name):
    data = get_npm_package_data_cached(package_name)

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
