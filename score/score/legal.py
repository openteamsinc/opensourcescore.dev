from score.notes import Note
from score.models import Source

LICENSE_LESS_PERMISSIVES = ["GPL", "AGPL", "LGPL", "Artistic", "CDDL", "MPL"]


def score_license(git_info: Source):

    license = git_info.license
    if git_info.error is not None:
        return

    if license is None:
        raise ValueError("License information is missing")

    if license.error:
        note = license.error
        yield note
        return

    if not license.license == "Unknown":
        yield Note.LICENSE_UNKNOWN

    if license.additional_text:
        yield Note.LICENSE_ADDITIONAL_TEXT

    if not license.spdx_id:
        yield Note.LICENSE_NOT_IN_SPDX

    if license.is_osi_approved is not True:
        yield Note.LICENSE_NOT_OSI_APPROVED

    if "derivative-work-copyleft" in license.restrictions:
        yield Note.LICENSE_DERIVATIVE_WORK_COPYLEFT
    if "network-copyleft" in license.restrictions:
        yield Note.LICENSE_NETWORK_COPYLEFT
    if "patent-grant" in license.restrictions:
        yield Note.LICENSE_PATENT_GRANT

    if "commercial-restrictions" in license.restrictions:
        yield Note.LICENSE_COMMERCIAL_RESTRICTIONS

    if "user-data-access" in license.restrictions:
        yield Note.LICENSE_USER_DATA_ACCESS
    if "cryptographic-autonomy" in license.restrictions:
        yield Note.LICENSE_CRYPTOGRAPHIC_AUTONOMY

    if "weak-copyleft" in license.restrictions:
        yield Note.LICENSE_WEAK_COPYLEFT

    # if license.kind in LICENSE_LESS_PERMISSIVES:
    #     yield Note.LICENSE_LESS_PERMISSIVE

    if license.modified:
        yield Note.LICENSE_MODIFIED


def build_legal_score(git_info: Source):

    if git_info.error:
        yield git_info.error

    yield from score_license(git_info)

    return
