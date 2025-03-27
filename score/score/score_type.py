from typing import List
from dataclasses import dataclass, field
import logging

from ..notes import Note, SCORE_ORDER, ANY, HEALTHY, HEALTH, LEGAL, MATURE, MATURITY

log = logging.getLogger(__name__)


@dataclass
class Score:
    value: str
    group: str
    notes: List[int] = field(default_factory=list)

    def __init__(self, initial_value: str, group: str):
        super().__init__()
        self.value = initial_value
        self.group = group
        self.notes = []

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
        if note.group == ANY or note.group == self.group:
            self.limit(note.category)
            self.notes.append(note)

    def dict(self):
        return {"value": self.value, "notes": [n.value for n in self.notes]}

    def dict_string_notes(self):
        return {"value": self.value, "notes": [n.name for n in self.notes]}

    @classmethod
    def legal(cls, notes):
        score = cls(HEALTHY, LEGAL)
        for note in notes:
            score.add_note(note)
        return score

    @classmethod
    def health_risk(cls, notes):
        score = cls(HEALTHY, HEALTH)
        for note in notes:
            score.add_note(note)
        return score

    @classmethod
    def maturity(cls, notes):
        score = cls(MATURE, MATURITY)
        for note in notes:
            score.add_note(note)
        return score
