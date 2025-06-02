from dataclasses import dataclass, field

from typing import Optional, List, Tuple
from datetime import datetime


@dataclass
class NoteDescr:
    code: str
    category: str
    description: str
    group: str
    oss_risk: Optional[str]


@dataclass
class Dependency:
    name: str
    specifiers: List[str]
    include_check: Optional[str] = None


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
    dependencies: Optional[List[Dependency]] = None


@dataclass
class License:
    error: Optional[str] = None
    license: Optional[str] = None
    kind: Optional[str] = None
    best_match: Optional[str] = None
    similarity: Optional[float] = None
    modified: bool = False
    diff: Optional[str] = None
    md5: Optional[str] = None
    # Additional fields for license metadata
    name: Optional[str] = None
    restrictions: List[str] = field(default_factory=list)
    additional_text: Optional[str] = None
    spdx_id: Optional[str] = None
    is_osi_approved: Optional[bool] = None


@dataclass
class Source:
    source_url: str

    error: Optional[str] = None
    license: Optional[License] = None

    package_destinations: List[Tuple[str, str]] = field(default_factory=list)

    recent_authors_count: Optional[int] = None
    max_monthly_authors_count: Optional[int] = None
    first_commit: Optional[datetime] = None
    latest_commit: Optional[datetime] = None


@dataclass
class CategorizedScore:
    value: str
    notes: list[str] = field(default_factory=list)


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
    error: Optional[str] = None
    vulns: list[Vulnerability] = field(default_factory=list)


@dataclass
class Score:
    legal: CategorizedScore
    health_risk: CategorizedScore
    maturity: CategorizedScore
    security: CategorizedScore
    notes: list[str] = field(default_factory=list)
