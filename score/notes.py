import os
import csv
from pathlib import Path
from typing import Dict, TypedDict, Optional

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
SECURITY = "Security"

GROUPS = {
    HEALTH: RISKS,
    LEGAL: RISKS,
    SECURITY: RISKS,
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
LONG_TIME_TO_FIX = 600


class Note:
    # Type annotation for _data as a list of dictionaries
    class NoteData(TypedDict):
        code: str
        group: str
        category: str
        description: str
        oss_risk: Optional[str]

    _data: Dict[str, NoteData] = {}

    @classmethod
    def load_csv(cls):
        current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        csv_path = current_dir / "notes.csv"

        with open(csv_path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            csv_content = {}

            for row in reader:
                if row["oss_risk"] == "":
                    row["oss_risk"] = None
                csv_content[row["code"]] = row

        cls._data = csv_content


def to_dict():
    if not Note._data:
        Note.load_csv()

    return Note._data


# Load CSV data when module is imported
Note.load_csv()

# Add static attributes to Note class for all note codes
for code in Note._data.keys():
    setattr(Note, code, code)


if __name__ == "__main__":
    # Generate notes.pyi stub file for better type checking

    # Load the CSV to get all note codes
    Note.load_csv()

    # Generate the stub file content
    stub_content = """# This file was auto-generated
from typing import Dict, TypedDict, ClassVar

SCORE_ORDER: list[str]
GROUPS: Dict[str, list[str]]
RISKS: list[str]

ANY: str
HEALTH: str
LEGAL: str
MATURITY: str
SECURITY: str


PLACEHOLDER: str
HEALTHY: str
MATURE: str
CAUTION_NEEDED: str
MODERATE_RISK: str
HIGH_RISK: str
EXPERIMENTAL: str
STALE: str
UNKNOWN: str
LEGACY: str

FEW_MAX_MONTHLY_AUTHORS_CONST: int
LONG_TIME_TO_FIX: int

def to_dict() -> Dict[str, NoteData]:
    pass


class NoteData(TypedDict):
    code: str
    group: str
    category: str
    description: str
    oss_risk: str


class Note:
    _data: ClassVar[Dict[str, NoteData]]

    @classmethod
    def load_csv(cls) -> None:
        ...
"""

    # Add all note codes as class variables
    for code in Note._data.keys():
        stub_content += f"    {code}: ClassVar[str]\n"

    # Write the stub file next to the current file
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    stub_path = current_dir / "notes.pyi"

    with open(stub_path, "w") as f:
        f.write(stub_content)

    print(f"Generated type stub file at: {stub_path}")
