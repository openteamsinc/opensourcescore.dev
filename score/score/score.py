import pandas as pd
from typing import Optional


def safe_date_diff(a, b) -> Optional[pd.Timedelta]:
    if pd.isnull(a):
        return None
    if pd.isnull(b):
        return None

    # Convert timezone-naive datetimes to UTC
    if a.tzinfo is None:
        a = pd.to_datetime(a).tz_localize("UTC")
    if b.tzinfo is None:
        b = pd.to_datetime(b).tz_localize("UTC")

    return a - b
