from typing import List
from dataclasses import dataclass, field
import logging

from score.models import CategorizedScore
from score.notes import (
    Note,
    SCORE_ORDER,
    ANY,
    HEALTHY,
    HEALTH,
    LEGAL,
    MATURE,
    MATURITY,
    SECURITY,
)

log = logging.getLogger(__name__)


@dataclass
class ScoreBuilder:
    value: str
    group: str
    notes: List[str] = field(default_factory=list)

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

    def is_in_group(self, note: str):
        group = Note._data[note]["group"]
        return group == ANY or group == self.group

    def add_note(self, note: str):
        assert isinstance(
            note, str
        ), f"Note must be an instance of str, got {type(note)}"
        if note not in Note._data:
            raise ValueError(f"Note {note} is not a valid note code")
        if note in self.notes:
            return

        if not self.is_in_group(note):
            return

        category = Note._data[note]["category"]
        self.limit(category)
        self.notes.append(note)

    def dict(self):
        return {"value": self.value, "notes": [n.value for n in self.notes]}

    def asmodel(self):
        return CategorizedScore(value=self.value, notes=self.notes)

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

    @classmethod
    def security(cls, notes):
        score = cls(HEALTHY, SECURITY)
        for note in notes:
            score.add_note(note)
        return score
