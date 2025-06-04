from score.models import Source
from score.notes import Note

LICENSE_LESS_PERMISSIVES = ["GPL", "AGPL", "LGPL", "Artistic", "CDDL", "MPL"]


def score_license(git_info: Source):

    licenses = git_info.licenses
    if git_info.error is not None:
        return

    if not licenses:
        yield Note.NO_LICENSE
        return

    for license in licenses:

        if license.error:
            note = license.error
            yield note
            return

        if license.license == "Unknown":
            yield Note.LICENSE_UNKNOWN
            return

        if license.additional_text:
            yield Note.LICENSE_ADDITIONAL_TEXT

        if not license.spdx_id:
            yield Note.LICENSE_NOT_IN_SPDX

        if license.spdx_id and license.is_osi_approved is not True:
            yield Note.LICENSE_NOT_OSI_APPROVED

        if "derivative-work-copyleft" in license.restrictions:
            yield Note.LICENSE_RESTRICTION_DERIVATIVE_WORK_COPYLEFT

        if "network-copyleft" in license.restrictions:
            yield Note.LICENSE_RESTRICTION_NETWORK_COPYLEFT

        if "patent-grant" in license.restrictions:
            yield Note.LICENSE_RESTRICTION_PATENT_GRANT

        if "commercial-restrictions" in license.restrictions:
            yield Note.LICENSE_RESTRICTION_COMMERCIAL

        if "user-data-access" in license.restrictions:
            yield Note.LICENSE_RESTRICTION_USER_DATA_ACCESS

        if "cryptographic-autonomy" in license.restrictions:
            yield Note.LICENSE_RESTRICTION_CRYPTOGRAPHIC_AUTONOMY

        if "weak-copyleft" in license.restrictions:
            yield Note.LICENSE_RESTRICTION_WEAK_COPYLEFT

        if license.modified:
            yield Note.LICENSE_MODIFIED


def build_legal_score(git_info: Source):

    if git_info.error:
        yield git_info.error

    yield from score_license(git_info)

    return
