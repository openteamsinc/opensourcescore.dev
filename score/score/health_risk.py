import pandas as pd

SCORE_ORDER = ["Healthy", "Caution Needed", "Moderate Risk", "High Risk"]

HEALTHY = SCORE_ORDER.index("Healthy")
CAUTION_NEEDED = SCORE_ORDER.index("Caution Needed")
MODERATE_RISK = SCORE_ORDER.index("Moderate Risk")
HIGH_RISK = SCORE_ORDER.index("High Risk")

one_year_ago = pd.Timestamp.now() - pd.DateOffset(years=1)
three_years_ago = pd.Timestamp.now() - pd.DateOffset(years=3)
five_years_ago = pd.Timestamp.now() - pd.DateOffset(years=5)

LESS_PERMISSIVE_LICENSES = ["GPL", "AGPL", "LGPL", "Artistic", "CDDL", "MPL"]


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

    numeric_score = HEALTHY

    def LIMIT_SCORE(value):
        nonlocal numeric_score
        numeric_score = max(numeric_score, value)

    license_kind = git_info.license.get("kind")
    modified = git_info.license.get("modified")

    if git_info.license.get("error"):
        score["value"] = LIMIT_SCORE(MODERATE_RISK)
        note = git_info.license.get("error", "Could not retrieve licence information")
        score["notes"].append(note)

    elif not license_kind or license_kind == "Unknown":
        score["value"] = LIMIT_SCORE(MODERATE_RISK)
        note = git_info.license.get("error", "Could not detect open source license")
        score["notes"].append(note)

    if license_kind in LESS_PERMISSIVE_LICENSES:
        score["value"] = LIMIT_SCORE(CAUTION_NEEDED)
        score["notes"].append(
            "License may have usage restrictions. Review terms before implementation"
        )

    if modified:
        score["value"] = LIMIT_SCORE(CAUTION_NEEDED)
        score["notes"].append("License may have been modified from the original")

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
            "No one has contributed to this repository in the last year"
        )
    elif recent_count < 2:
        LIMIT_SCORE(CAUTION_NEEDED)
        score["notes"].append(
            "Only one author has contributed to this repository in the last year"
        )

    latest_commit_age = (pd.Timestamp.now() - git_info.latest_commit).days / 365.25

    if latest_commit_age < one_year_ago:
        LIMIT_SCORE(HEALTHY)
        score["notes"].append("Last commit was within the last year")
    elif one_year_ago <= latest_commit_age < three_years_ago:
        LIMIT_SCORE(CAUTION_NEEDED)
        score["notes"].append("Last commit was between 1 and 3 years ago")
    elif three_years_ago <= latest_commit_age < five_years_ago:
        LIMIT_SCORE(MODERATE_RISK)
        score["notes"].append("Last commit was between 3 and 5 years ago")
    else:
        LIMIT_SCORE(HIGH_RISK)
        score["notes"].append("Last commit was over 5 years ago")

    score["value"] = SCORE_ORDER[numeric_score]

    return score
