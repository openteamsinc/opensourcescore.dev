import enum
import pandas as pd

HEALTHY = "Healthy"
CAUTION_NEEDED = "Caution Needed"
MODERATE_RISK = "Moderate Risk"
HIGH_RISK = "High Risk"

LEGACY = "Legacy"
UNKNOWN = "Unknown"
PLACEHOLDER = "Placeholder"
MATURE = "Mature"

EXPERIMENTAL = "Experimental"

RISKS = [
    HEALTHY,
    CAUTION_NEEDED,
    MODERATE_RISK,
    HIGH_RISK,
]

GROUPS = {
    "Health": RISKS,
    "Legal": RISKS,
    "Maturuty": [
        HEALTHY,
        CAUTION_NEEDED,
        MODERATE_RISK,
        HIGH_RISK,
    ],
}
SCORE_ORDER = [
    HEALTHY,
    MATURE,
    CAUTION_NEEDED,
    MODERATE_RISK,
    HIGH_RISK,
    EXPERIMENTAL,
    LEGACY,
    UNKNOWN,
    PLACEHOLDER,
]


class Note(enum.Enum):

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, *dd):

        category, description = dd
        self.description = description
        self.category = category

    @classmethod
    def lookup(cls, note_id):
        if not hasattr(cls, "_lookup"):

            cls._lookup = {
                v.value: k for k, v in vars(cls).items() if isinstance(v, Note)
            }

        return cls._lookup.get(note_id, f"UNKNOWN_{note_id}")

    UNSAFE_GIT_PROTOCOL = UNKNOWN, "Unsafe Git Protocol"
    REPO_NOT_FOUND = MODERATE_RISK, "Repo not found"
    REPO_EMPTY = PLACEHOLDER, "Repository is empty"
    GIT_TIMEOUT = UNKNOWN, "Could not clone repo in a reasonable amount of time"
    OTHER_GIT_ERROR = UNKNOWN, "Could not clone repo"
    LICENSE_CHECKOUT_ERROR = MODERATE_RISK, "Could not checkout license"
    NO_LICENSE = MODERATE_RISK, "No License Found"
    NO_LICENSE_INFO = MODERATE_RISK, "Could not retrieve licence information"
    NO_OS_LICENSE = MODERATE_RISK, "Could not detect open source license"
    LESS_PERMISSIVE_LICENSE = (
        CAUTION_NEEDED,
        "License may have usage restrictions. Review terms before implementation",
    )
    LICENSE_MODIFIED = (
        CAUTION_NEEDED,
        "License may have been modified from the original",
    )

    INSECURE_CONNECTION = UNKNOWN, "Source code scheme 'http://' is not secure"
    LOCALHOST_URL = UNKNOWN, "Source code location is a localhost url"
    INVALID_URL = UNKNOWN, "Source code location is not a valid url"

    FEW_MAX_MONTHLY_AUTHORS = (
        CAUTION_NEEDED,
        "Few authors have contributed to this repository in a single month",
    )

    NO_AUTHORS_THIS_YEAR = (
        CAUTION_NEEDED,
        "No one has contributed to this repository in the last year",
    )
    ONE_AUTHORS_THIS_YEAR = (
        CAUTION_NEEDED,
        "Only one author has contributed to this repository in the last year",
    )

    LAST_COMMIT_5_YEARS = (
        HIGH_RISK,
        "The last commit to source control was over 5 years ago",
    )

    NO_PROJECT_NAME = (
        CAUTION_NEEDED,
        "Could not confirm the published package name from the source code",
    )
    PROJECT_NOT_PUBLISHED = (
        CAUTION_NEEDED,
        "The Python package name from the source code is not a published package",
    )

    PACKAGE_NAME_MISMATCH = (
        HIGH_RISK,
        "published package has a different name than specified in the source code",
    )

    NO_COMMITS = PLACEHOLDER, "There are no human commits in this repository"

    FIRST_COMMIT_THIS_YEAR = EXPERIMENTAL, "First commit in the last year"

    LAST_COMMIT_OVER_A_YEAR = LEGACY, "The last commit was over a year ago"

    PACKGE_SKEW_NOT_UPDATED = (
        MODERATE_RISK,
        "Package is at least a year behind the the source code",
    )

    PACKGE_SKEW_NOT_RELEASED = (
        MODERATE_RISK,
        "Package is at least a year ahead of the source code",
    )


def to_dict():
    return {
        v.value: {
            "code": k,
            "category": v.category,
            "description": v.description,
            "id": v.value,
        }
        for k, v in vars(Note).items()
        if isinstance(v, Note)
    }


def to_df():
    return pd.DataFrame.from_records(
        [
            (k, v.value, v.category, v.description)
            for k, v in vars(Note).items()
            if isinstance(v, Note)
        ],
        columns=["code", "id", "category", "description"],
    ).set_index("id")
