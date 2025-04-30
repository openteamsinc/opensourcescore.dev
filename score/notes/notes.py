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


FEW_MAX_MONTHLY_AUTHORS_CONST = 3
LONG_TIME_TO_FIX = 600


def to_dict():
    if not Note._data:
        Note.load_csv()

    return Note._data
