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
STALE = "Stale"
EXPERIMENTAL = "Experimental"

RISKS = [
    HEALTHY,
    CAUTION_NEEDED,
    MODERATE_RISK,
    HIGH_RISK,
]

ANY = "Any"
HEALTH = "Health"
LEGAL = "Legal"
MATURITY = "Maturity"

GROUPS = {
    HEALTH: RISKS,
    LEGAL: RISKS,
    MATURITY: [
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
    STALE,
    LEGACY,
    UNKNOWN,
    PLACEHOLDER,
]

FEW_MAX_MONTHLY_AUTHORS_CONST = 3


class Note(enum.Enum):

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, *dd):
        if len(dd) != 3:
            raise ValueError(
                f"Note must be initialized with 3 parameters, got {len(dd)}"
            )
        group, category, description = dd
        self.description = description
        self.category = category
        self.group = group

    @classmethod
    def lookup(cls, note_id):
        if not hasattr(cls, "_lookup"):

            cls._lookup = {
                v.value: k for k, v in vars(cls).items() if isinstance(v, Note)
            }

        return cls._lookup.get(note_id, f"UNKNOWN_{note_id}")

    UNSAFE_GIT_PROTOCOL = ANY, UNKNOWN, "Unsafe Git Protocol"
    REPO_NOT_FOUND = ANY, MODERATE_RISK, "Repo not found"
    REPO_EMPTY = ANY, PLACEHOLDER, "Repository is empty"
    GIT_TIMEOUT = ANY, UNKNOWN, "Could not clone repo in a reasonable amount of time"
    OTHER_GIT_ERROR = ANY, UNKNOWN, "Could not clone repo"
    LICENSE_CHECKOUT_ERROR = LEGAL, MODERATE_RISK, "Could not checkout license"
    NO_LICENSE = LEGAL, MODERATE_RISK, "No License Found"
    NO_LICENSE_INFO = LEGAL, MODERATE_RISK, "Could not retrieve licence information"
    NO_OS_LICENSE = (
        LEGAL,
        MODERATE_RISK,
        "License may not comply with open source standards",
    )
    LESS_PERMISSIVE_LICENSE = (
        LEGAL,
        CAUTION_NEEDED,
        "License may have usage restrictions. Review terms before implementation",
    )
    LICENSE_MODIFIED = (
        LEGAL,
        CAUTION_NEEDED,
        "License may have been modified from the original",
    )

    INSECURE_CONNECTION = ANY, UNKNOWN, "Source code scheme 'http://' is not secure"
    LOCALHOST_URL = ANY, UNKNOWN, "Source code location is a localhost url"
    INVALID_URL = ANY, UNKNOWN, "Source code location is not a valid url"

    FEW_MAX_MONTHLY_AUTHORS = (
        HEALTH,
        MODERATE_RISK,
        f"Fewer than {FEW_MAX_MONTHLY_AUTHORS_CONST} authors have contributed to this repository",
    )

    ONE_AUTHORS_THIS_YEAR = (
        HEALTH,
        CAUTION_NEEDED,
        "Only one author has contributed to this repository in the last year",
    )

    LAST_COMMIT_OVER_5_YEARS = (
        MATURITY,
        LEGACY,
        "The last commit to source control was over 5 years ago",
    )

    NO_PROJECT_NAME = (
        HEALTH,
        CAUTION_NEEDED,
        "Could not confirm the published package name from the source code",
    )
    PROJECT_NOT_PUBLISHED = (
        HEALTH,
        CAUTION_NEEDED,
        "The Python package name from the source code is not a published package",
    )

    PACKAGE_NAME_MISMATCH = (
        HEALTH,
        HIGH_RISK,
        "published package has a different name than specified in the source code",
    )

    NO_COMMITS = ANY, PLACEHOLDER, "There are no human commits in this repository"

    FIRST_COMMIT_THIS_YEAR = MATURITY, EXPERIMENTAL, "First commit in the last year"

    LAST_COMMIT_OVER_A_YEAR = MATURITY, STALE, "The last commit was over a year ago"

    PACKAGE_SKEW_NOT_UPDATED = (
        HEALTH,
        MODERATE_RISK,
        "Package is at least a year behind the the source code",
    )

    PACKAGE_SKEW_NOT_RELEASED = (
        HEALTH,
        MODERATE_RISK,
        "Package is at least a year ahead of the source code",
    )

    PACKAGE_LICENSE_MISMATCH = (
        LEGAL,
        MODERATE_RISK,
        "Package license does not match the source code license",
    )

    PACKAGE_NO_LICENSE = (
        LEGAL,
        MODERATE_RISK,
        "Package was not published with a license",
    )

    PACKAGE_SOURCE_NOT_FOUND = (
        ANY,
        HIGH_RISK,
        "The source code location could not be found",
    )
    HEALTHY = ANY, HEALTHY, "Healthy"


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
