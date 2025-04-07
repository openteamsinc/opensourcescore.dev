from typing import Optional
from datetime import datetime
from dateutil.parser import parse as parse_date
import logging

log = logging.getLogger(__name__)


def try_parse_date(date_str: Optional[str]) -> Optional[datetime]:
    if not date_str:
        return None

    try:
        return parse_date(date_str)
    except Exception as e:
        log.error(f"Failed to parse date {date_str}: {e}")
        return None
