import logging
from dataclasses import dataclass, field
from typing import List

from score.models import CategorizedScore
from score.notes import Note, ScoreCategories, ScoreGroups

log = logging.getLogger(__name__)


@dataclass
class ScoreBuilder:
    value: str
    group: str
    notes: List[str] = field(default_factory=list)

    def __init__(self, initial_value: str, group: str):
        assert (
            initial_value in ScoreCategories.values()
        ), f"Invalid initial value: '{initial_value}'"
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

        SCORE_ORDER = ScoreCategories.values()
        current_numeric_score = SCORE_ORDER.index(self.value)
        new_numeric_score = SCORE_ORDER.index(new_score)
        self.value = SCORE_ORDER[max(current_numeric_score, new_numeric_score)]

    def is_in_group(self, note: str):
        group = Note._data[note]["group"]
        return group == ScoreGroups.ANY.value or group == self.group

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
        return {"value": self.value, "notes": self.notes}

    def asmodel(self):
        return CategorizedScore(value=self.value, notes=self.notes)

    @classmethod
    def legal(cls, notes):
        score = cls(ScoreCategories.HEALTHY.value, ScoreGroups.LEGAL.value)
        for note in notes:
            score.add_note(note)
        return score

    @classmethod
    def health_risk(cls, notes):
        score = cls(ScoreCategories.HEALTHY.value, ScoreGroups.HEALTH.value)
        for note in notes:
            score.add_note(note)
        return score

    @classmethod
    def maturity(cls, notes):
        score = cls(ScoreCategories.MATURE.value, ScoreGroups.MATURITY.value)
        for note in notes:
            score.add_note(note)
        return score

    @classmethod
    def security(cls, notes):
        score = cls(ScoreCategories.HEALTHY.value, ScoreGroups.SECURITY.value)
        for note in notes:
            score.add_note(note)
        return score
