from dataclasses import dataclass, field
from pydantic import field_serializer
from typing import Optional, List, Tuple
from datetime import datetime
from .notes import Note


@dataclass
class NoteDescr:
    code: str
    category: str
    description: str
    id: int


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

    package_destinations: List[Tuple[str, str]] = field(default_factory=list)

    recent_authors_count: Optional[int] = None
    max_monthly_authors_count: Optional[int] = None
    first_commit: Optional[datetime] = None
    latest_commit: Optional[datetime] = None


@dataclass
class CategorizedScore:
    value: str
    notes: list[Note] = field(default_factory=list)

    @field_serializer("notes")
    def serialize_notes(self, notes):
        return [note.name for note in notes]


@dataclass
class Vulnerability:
    id: str
    published_on: datetime
    fixed_on: Optional[datetime]
    severity: str
    severity_num: Optional[float]
    days_to_fix: Optional[int]


@dataclass
class Vulnerabilities:
    error: Optional[Note] = None
    vulns: list[Vulnerability] = field(default_factory=list)


@dataclass
class Score:
    legal: CategorizedScore
    health_risk: CategorizedScore
    maturity: CategorizedScore
    security: CategorizedScore
    notes: list[Note] = field(default_factory=list)

    @field_serializer("notes")
    def serialize_notes(self, notes):
        return [note.name for note in notes]
