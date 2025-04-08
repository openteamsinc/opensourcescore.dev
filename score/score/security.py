from typing import Iterator, Optional
from datetime import datetime, timedelta, timezone
from score.notes import Note, LONG_TIME_TO_FIX
from score.models import Vulnerabilities


ONE_YEAR_AGO = datetime.now(tz=timezone.utc) - timedelta(days=365)


def median(lst: list[int]) -> Optional[int]:
    """Calculate the median of a list of integers."""
    if not lst:
        return None
    if len(lst) == 1:
        return lst[0]

    sorted_lst = sorted(lst)
    n = len(sorted_lst)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_lst[mid - 1] + sorted_lst[mid]) // 2
    else:
        return sorted_lst[mid]


def score_security(vulns: Vulnerabilities) -> Iterator[Note]:
    days_to_fix = [v.days_to_fix for v in vulns.vulns if v.days_to_fix is not None]

    median_days_to_fix = median(days_to_fix)

    if median_days_to_fix and median_days_to_fix > LONG_TIME_TO_FIX:
        yield Note.VULNERABILITIES_LONG_TIME_TO_FIX

    recent_cutoff = datetime.now(tz=timezone.utc) - timedelta(days=LONG_TIME_TO_FIX)
    recent = [v for v in vulns.vulns if v.published_on > recent_cutoff]

    if len(recent) > 2:
        yield Note.VULNERABILITIES_RECENT

    if len([v for v in recent if v.severity_num and v.severity_num >= 7]):
        yield Note.VULNERABILITIES_SEVERE

    return None
