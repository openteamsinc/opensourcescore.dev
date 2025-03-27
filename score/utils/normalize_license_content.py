import re


def normalize_license_content(content: str):
    normalized = re.sub(r"\s+", " ", content).strip()
    return normalized
