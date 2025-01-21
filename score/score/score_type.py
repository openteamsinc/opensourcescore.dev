from typing import List, Optional
from dataclasses import dataclass, field
import logging

from ..notes import Note

log = logging.getLogger(__name__)

HEALTHY = "Healthy"
CAUTION_NEEDED = "Caution Needed"
MODERATE_RISK = "Moderate Risk"
HIGH_RISK = "High Risk"
SCORE_ORDER = [HEALTHY, CAUTION_NEEDED, MODERATE_RISK, HIGH_RISK]


@dataclass
class Score:
    value: Optional[str] = HEALTHY
    notes: List[int] = field(default_factory=list)

    def limit(self, new_score: str):
        if self.value is None:
            self.value = new_score
            return
        if self.value == "Unknown":
            return

        current_numeric_score = SCORE_ORDER.index(self.value)
        new_numeric_score = SCORE_ORDER.index(new_score)
        self.value = SCORE_ORDER[max(current_numeric_score, new_numeric_score)]

    def dict(self):
        return {"value": self.value, "notes": self.notes}

    def dict_string_notes(self):
        return {"value": self.value, "notes": [Note.lookup(n) for n in self.notes]}
