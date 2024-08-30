SCORE_ORDER = ["Healthy", "Caution Needed", "Moderate Risk", "High Risk"]

HEALTHY = SCORE_ORDER.index("Healthy")
CAUTION_NEEDED = SCORE_ORDER.index("Caution Needed")
MODERATE_RISK = SCORE_ORDER.index("Moderate Risk")
HIGH_RISK = SCORE_ORDER.index("High Risk")

LESS_PERMISSIVE_LICENSES = ["GPL", "AGPL", "LGPL", "SSPL", "CDDL", "MPL", "EPL"]


def build_health_risk_score(source_url, git_info):
    score = {"value": "Healthy", "notes": []}

    if git_info.error:
        score["value"] = "Unknown"
        score["notes"].append(git_info.error)
        return score

    if git_info.first_commit == "NaT":
        score["value"] = "Placeholder"
        score["notes"].append("There are no human commits in this repository")
        return score

    license_type = git_info.license.get("license")
    if not license_type or license_type == "Unknown" or git_info.license.get("error"):
        score["value"] = "Moderate Risk"
        score["notes"].append("No license specified.")
    elif any(license in license_type for license in LESS_PERMISSIVE_LICENSES):
        score["value"] = "Caution Needed"
        score["notes"].append(
            "Less permissive license. Further investigation needed for proprietary projects."
        )

    numeric_score = HEALTHY

    def LIMIT_SCORE(value):
        nonlocal numeric_score
        numeric_score = max(numeric_score, value)

    mma_count = git_info["max_monthly_authors_count"]
    recent_count = git_info["recent_authors_count"]

    if mma_count < 3:
        LIMIT_SCORE(CAUTION_NEEDED)
        score["notes"].append(
            f"Only {mma_count} author(s) have contributed to this repository in a single month"
        )

    if recent_count < 1:
        LIMIT_SCORE(CAUTION_NEEDED)
        score["notes"].append(
            "Noone has contributed to this repository in the last year"
        )
    elif recent_count < 2:
        LIMIT_SCORE(CAUTION_NEEDED)
        score["notes"].append(
            "Only one author has contributed to this repository in the last year"
        )

    score["value"] = SCORE_ORDER[numeric_score]

    return score
