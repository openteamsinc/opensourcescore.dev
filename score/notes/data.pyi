# This file was auto-generated
from typing import ClassVar, Dict, TypedDict

class NoteData(TypedDict):
    code: str
    group: str
    category: str
    description: str
    oss_risk: str

class Note:
    _data: ClassVar[Dict[str, NoteData]]

    @classmethod
    def load_csv(cls) -> None: ...
    NO_SOURCE_UNSAFE_GIT_PROTOCOL: ClassVar[str]
    REPO_EMPTY: ClassVar[str]
    NO_SOURCE_REPO_NOT_FOUND: ClassVar[str]
    NO_SOURCE_GIT_TIMEOUT: ClassVar[str]
    NO_SOURCE_OTHER_GIT_ERROR: ClassVar[str]
    NO_LICENSE: ClassVar[str]
    COMPLEX_LICENSE: ClassVar[str]
    LICENSE_NOT_OSS: ClassVar[str]
    LICENSE_LESS_PERMISSIVE: ClassVar[str]
    LICENSE_MODIFIED: ClassVar[str]
    NO_SOURCE_INSECURE_CONNECTION: ClassVar[str]
    NO_SOURCE_LOCALHOST_URL: ClassVar[str]
    NO_SOURCE_INVALID_URL: ClassVar[str]
    FEW_MAX_MONTHLY_AUTHORS: ClassVar[str]
    ONE_AUTHOR_THIS_YEAR: ClassVar[str]
    LAST_COMMIT_OVER_5_YEARS: ClassVar[str]
    NO_PROJECT_NAME: ClassVar[str]
    PROJECT_NOT_PUBLISHED: ClassVar[str]
    PACKAGE_NAME_MISMATCH: ClassVar[str]
    NO_COMMITS: ClassVar[str]
    FIRST_COMMIT_THIS_YEAR: ClassVar[str]
    LAST_COMMIT_OVER_A_YEAR: ClassVar[str]
    PACKAGE_SKEW_NOT_UPDATED: ClassVar[str]
    PACKAGE_SKEW_NOT_RELEASED: ClassVar[str]
    PACKAGE_LICENSE_MISMATCH: ClassVar[str]
    PACKAGE_NO_LICENSE: ClassVar[str]
    NO_SOURCE_URL: ClassVar[str]
    VULNERABILITIES_CHECK_FAILED: ClassVar[str]
    VULNERABILITIES_LONG_TIME_TO_FIX: ClassVar[str]
    VULNERABILITIES_RECENT: ClassVar[str]
    VULNERABILITIES_SEVERE: ClassVar[str]
    HEALTHY: ClassVar[str]
    PENDING: ClassVar[str]
    ERROR: ClassVar[str]
    NOT_OPEN_SOURCE: ClassVar[str]
    LICENSE_UNKNOWN: ClassVar[str]
    LICENSE_ADDITIONAL_TEXT: ClassVar[str]
    LICENSE_NOT_IN_SPDX: ClassVar[str]
    LICENSE_NOT_OSI_APPROVED: ClassVar[str]
    LICENSE_RESTRICTION_DERIVATIVE_WORK_COPYLEFT: ClassVar[str]
    LICENSE_RESTRICTION_NETWORK_COPYLEFT: ClassVar[str]
    LICENSE_RESTRICTION_PATENT_GRANT: ClassVar[str]
    LICENSE_RESTRICTION_COMMERCIAL: ClassVar[str]
    LICENSE_RESTRICTION_USER_DATA_ACCESS: ClassVar[str]
    LICENSE_RESTRICTION_CRYPTOGRAPHIC_AUTONOMY: ClassVar[str]
    LICENSE_RESTRICTION_WEAK_COPYLEFT: ClassVar[str]
    PACKAGE_LICENSE_NOT_SPDX_ID: ClassVar[str]
    NO_SOURCE_PRIVATE_REPO: ClassVar[str]
