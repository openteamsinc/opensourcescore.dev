SCORE_ORDER = ["Healthy", "Caution Needed", "Moderate Risk", "High Risk"]

HEALTHY = SCORE_ORDER.index("Healthy")
CAUTION_NEEDED = SCORE_ORDER.index("Caution Needed")
MODERATE_RISK = SCORE_ORDER.index("Moderate Risk")
HIGH_RISK = SCORE_ORDER.index("High Risk")


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

    if git_info.license.get("error") or git_info.license["license"] == "Unknown":
        score["value"] = "Moderate Risk"
        score["notes"].append("License could not be determined")
        return score

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
