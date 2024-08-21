import pandas as pd

one_year_ago = pd.Timestamp.now() - pd.DateOffset(years=1)


def build_maturity_score(source_url, git_info):
    score = {"value": "Mature", "notes": []}
    if git_info.error:
        score["value"] = "Unknown"
        score["notes"].append(git_info.error)
        return score

    if git_info.first_commit == "NaT":
        score["value"] = "Placeholder"
        score["notes"].append("There are no human commits in this repository")
        return score

    if git_info.latest_commit < one_year_ago:
        days_since_last_commit = (pd.Timestamp.now() - git_info.latest_commit).days
        score["value"] = "Legacy"
        score["notes"].append(
            f"The last commit was over {days_since_last_commit} days ago"
        )
    if git_info.first_commit > one_year_ago:
        score["value"] = "Experimental"
        score["notes"].append("First commit in the last year")

    return score
