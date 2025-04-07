from score.notes import Note
from score.models import Source

LICENSE_LESS_PERMISSIVES = ["GPL", "AGPL", "LGPL", "Artistic", "CDDL", "MPL"]


def score_license(git_info: Source):

    license = git_info.license
    if license is None:
        raise ValueError("License information is missing")

    if license.error:
        note = license.error
        yield note
        return

    if not license.kind or license.kind == "Unknown":
        yield Note.LICENSE_NOT_OSS

    if license.kind in LICENSE_LESS_PERMISSIVES:
        yield Note.LICENSE_LESS_PERMISSIVE

    if license.modified:
        yield Note.LICENSE_MODIFIED


def build_legal_score(git_info: Source):

    if git_info.error:
        yield git_info.error

    yield from score_license(git_info)

    return
