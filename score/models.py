from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from .notes import Note


@dataclass
class Package:
    name: str
    ecosystem: str
    version: Optional[str] = None
    license: Optional[str] = None
    source_url: Optional[str] = None
    source_url_key: Optional[str] = None
    release_date: Optional[datetime] = None
    status: str = "ok"


@dataclass
class License:
    error: Optional[Note] = None
    license: Optional[str] = None
    kind: Optional[str] = None
    best_match: Optional[str] = None
    similarity: Optional[float] = None
    modified: bool = False
    diff: Optional[str] = None
    md5: Optional[str] = None


@dataclass
class Source:
    source_url: str

    error: Optional[Note] = None
    license: Optional[License] = None

    package_destinations: list[list[str]] = field(default_factory=list)

    recent_authors_count: Optional[int] = None
    max_monthly_authors_count: Optional[int] = None
    first_commit: Optional[datetime] = None
    latest_commit: Optional[datetime] = None


@dataclass
class CategorizedScore:
    value: Optional[str] = None
    notes: list[Note] = field(default_factory=list)


@dataclass
class Score:
    notes: list[Note] = field(default_factory=list)
    legal: CategorizedScore = field(
        default_factory=lambda: CategorizedScore(notes=[], value=None)
    )
    health_risk: CategorizedScore = field(
        default_factory=lambda: CategorizedScore(notes=[], value=None)
    )
    maturity: CategorizedScore = field(
        default_factory=lambda: CategorizedScore(notes=[], value=None)
    )
