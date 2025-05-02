from enum import Enum
from .data import Note


ANY = "Any"
HEALTH = "Health"
LEGAL = "Legal"
MATURITY = "Maturity"
SECURITY = "Security"


class ScoreGroups(Enum):
    ANY = "Any"
    HEALTH = "Health"
    LEGAL = "Legal"
    MATURITY = "Maturity"
    SECURITY = "Security"

    @classmethod
    def values(cls):
        return [member.value for member in cls]


class ScoreCategories(Enum):
    HEALTHY = "Healthy"
    MATURE = "Mature"
    CAUTION_NEEDED = "Caution Needed"
    MODERATE_RISK = "Moderate Risk"
    HIGH_RISK = "High Risk"
    EXPERIMENTAL = "Experimental"
    STALE = "Stale"
    LEGACY = "Legacy"
    PLACEHOLDER = "Placeholder"
    UNKNOWN = "Unknown"
    PENDING = "Pending"
    ERROR = "Error"

    @classmethod
    def values(cls):
        return [member.value for member in cls]


FEW_MAX_MONTHLY_AUTHORS_CONST = 3
LONG_TIME_TO_FIX = 600


def to_dict():
    if not Note._data:
        Note.load_csv()

    return Note._data


def _validate_data():
    for key, value in Note._data.items():
        assert (
            value["group"] in ScoreGroups.values()
        ), f"Invalid group '{value['group']}' for note '{key}'"
        assert (
            value["category"] in ScoreCategories.values()
        ), f"Invalid category '{value['category']}' for note '{key}'"


_validate_data()
