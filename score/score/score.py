from duckdb import DuckDBPyConnection as Conn
import pandas as pd
from tqdm import tqdm
import pyarrow as pa

from .maturity import build_maturity_score
from .health_risk import build_health_risk_score


ecosystem_schema = pa.struct(
    [("pypi", pa.string()), ("npm", pa.string()), ("conda", pa.string())]
)

package_schema = pa.struct(
    [("ecosystem", pa.string()), ("name", pa.string()), ("version", pa.string())]
)

assessment_schema = pa.struct(
    [("notes", pa.list_(pa.string())), ("value", pa.string())]
)

score_schema = pa.schema(
    [
        ("source_url", pa.string()),
        ("packages", pa.list_(package_schema)),
        ("ecosystem_destination", ecosystem_schema),
        ("maturity", assessment_schema),
        ("health_risk", assessment_schema),
    ]
)


def fmt_pypi(p):
    return {
        "name": p["name"],
        "version": p["version"],
        "ecosystem": "PyPI",
    }


def fmt_conda(p):
    return {
        "name": p["full_name"],
        "version": p["latest_version"],
        "ecosystem": "conda",
    }


def build_score(source_url, row):
    score: dict = {
        "source_url": source_url,
        "packages": [],
        "ecosystem_destination": {"pypi": row.py_package, "npm": None, "conda": None},
    }

    score["packages"].extend([fmt_pypi(p) for p in row.pypi_packages])
    score["packages"].extend([fmt_conda(c) for c in row.conda_packages])
    score["maturity"] = build_maturity_score(source_url, row)
    score["health_risk"] = build_health_risk_score(row).dict()

    return score


def create_scores(db: Conn):
    df = db.query(
        """
SELECT
    g.*,
    array(SELECT p FROM pypi as p WHERE p.source_url = g.source_url) AS pypi_packages,
    array(SELECT c FROM conda as c WHERE c.source_url = g.source_url) AS conda_packages
FROM
    git as g
WHERE
    g.source_url IS NOT NULL
    """
    ).df()
    df = df[~df.source_url.isna()]
    df.set_index("source_url", inplace=True)

    scores = []
    for source_url, row in tqdm(df.iterrows(), total=df.index.size, disable=None):
        score = build_score(source_url, row)
        scores.append(score)
    df = pd.DataFrame(scores)
    return df
