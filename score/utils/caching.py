import os
import json
import logging
from dataclasses import asdict
from dacite import from_dict, Config
from typing import Optional, TypeVar, Type, Any, Tuple
from datetime import datetime, timezone
import fsspec
from score.notes import Note


CACHE_LOCATION = os.environ.get("CACHE_LOCATION", "gs://openteams-score-data/cache")

protocol = CACHE_LOCATION.split("://")[0] if "://" in CACHE_LOCATION else "file"
fs = fsspec.filesystem(protocol)

log = logging.getLogger(__name__)


def cache_path(suffix: str):
    return f"{CACHE_LOCATION}/{suffix}"


def cache_hit(filename, days=1):
    try:
        stat = fs.stat(filename)
    except FileNotFoundError:
        return False
    age = datetime.now(tz=timezone.utc) - stat["mtime"]
    return age.days <= days


T = TypeVar("T")


def load_from_cache(datacls: Type[T], cache_filename: str) -> Optional[T]:
    try:
        with fs.open(cache_filename, "r") as fp:
            data = json.load(fp)
        pkg = from_dict(
            datacls,
            data,
            config=Config(
                type_hooks={
                    datetime: datetime.fromisoformat,
                    Note: lambda x: getattr(Note, x),
                    Tuple[str, str]: tuple,  # type: ignore
                }
            ),
        )
        log.info(f"Cache hit for {cache_filename}")
        return pkg
    except Exception:
        log.exception("Failed to load package data from cache. fetching package data")

    return None


def save_to_cache(data: Any, cache_filename: str) -> None:
    dict_data = asdict(data)
    with fs.open(cache_filename, "w") as fp:
        json.dump(dict_data, fp, default=default_with_datetime)


def default_with_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Note):
        return obj.name
    raise TypeError(f"Type {type(obj)} not serializable")
