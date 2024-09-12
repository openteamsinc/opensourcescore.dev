import enum
import pandas as pd


class Note(enum.Enum):

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, note):
        self.note = note

    UNSAFE_GIT_PROTOCOL = "Unsafe Git Protocol"
    REPO_NOT_FOUND = "Repo not found"
    REPO_EMPTY = "Repository is empty"
    GIT_TIMEOUT = "Could not clone repo in a reasonable amount of time"
    OTHER_GIT_ERROR = "Could not clone repo"
    LICENSE_CHECKOUT_ERROR = "Could not checkout license"
    NO_LICENSE = "No License Found"
    NO_LICENSE_INFO = "Could not retrieve licence information"
    NO_OS_LICENSE = "Could not detect open source license"
    LESS_PERMISSIVE_LICENSE = (
        "License may have usage restrictions. Review terms before implementation"
    )
    LICENSE_MODIFIED = "License may have been modified from the original"

    INSECURE_CONNECTION = "Source code scheme 'http://' is not secure"
    LOCALHOST_URL = "Source code location is a localhost url"
    INVALID_URL = "Source code location is not a valid url"

    FEW_MAX_MONTHLY_AUTHORS = (
        "Few authors have contributed to this repository in a single month"
    )

    NO_AUTHORS_THIS_YEAR = "No one has contributed to this repository in the last year"
    ONE_AUTHORS_THIS_YEAR = (
        "Only one author has contributed to this repository in the last year"
    )

    LAST_COMMIT_5_YEARS = "The last commit to source control was over 5 years ago"

    NO_PROJECT_NAME = (
        "Could not confirm the published package name from the source code"
    )
    PROJECT_NOT_PUBLISHED = (
        "The Python package name from the source code is not a published package"
    )

    PACKAGE_NAME_MISMATCH = (
        "published package has a different name than specified in the source code"
    )

    NO_COMMITS = "There are no human commits in this repository"

    FIRST_COMMIT_THIS_YEAR = "First commit in the last year"

    LAST_COMMIT_OVER_A_YEAR = "The last commit was over a year ago"

    PACKGE_SKEW_NOT_UPDATED = "Package is out of sync with the source code"

    PACKGE_SKEW_NOT_RELEASED = "Package is ahead of the source code"


def to_df():
    return pd.DataFrame.from_records(
        [(k, v.value, v.note) for k, v in vars(Note).items() if not k.startswith("_")],
        columns=["code", "id", "note"],
    ).set_index("id")
