import csv
import os
from pathlib import Path
from typing import Dict, Optional, TypedDict


class Note:
    # Type annotation for _data as a list of dictionaries
    class NoteData(TypedDict):
        code: str
        group: str
        category: str
        description: str
        oss_risk: Optional[str]

    _data: Dict[str, NoteData] = {}


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


# Load CSV data when module is imported
load_csv(Note)

# Add static attributes to Note class for all note codes
for code in Note._data.keys():
    setattr(Note, code, code)


if __name__ == "__main__":
    # Generate notes.pyi stub file for better type checking

    load_csv(Note)

    # Generate the stub file content
    stub_content = """# This file was auto-generated
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
"""

    # Add all note codes as class variables
    for code in Note._data.keys():
        stub_content += f"    {code}: ClassVar[str]\n"

    # Write the stub file next to the current file
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    stub_path = current_dir / "data.pyi"

    with open(stub_path, "w") as f:
        f.write(stub_content)

    print(f"Generated type stub file at: {stub_path}")
