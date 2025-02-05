from typing import List, Optional
from dataclasses import dataclass, field
import logging

from ..notes import Note, SCORE_ORDER, HEALTHY

log = logging.getLogger(__name__)


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

    def add_note(self, note: Note):
        assert isinstance(note, Note), f"Note must be an instance of Note, got {note}"
        self.limit(note.category)
        self.notes.append(note)

    def dict(self):
        return {"value": self.value, "notes": [n.value for n in self.notes]}

    def dict_string_notes(self):
        return {"value": self.value, "notes": [n.name for n in self.notes]}
