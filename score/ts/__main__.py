from datetime import datetime
from score.app import ScoreResponse, NotesResponse
from score.notes import Note
from .generate import TypescriptGenerator

generator = TypescriptGenerator()
generator = generator.register(datetime, "string")
generator = generator.register(Note, "string")
generator = generator.update(ScoreResponse)
generator = generator.update(NotesResponse)
print(generator.dump())
