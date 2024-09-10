import os
from typing import Iterable, Any
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor


@lru_cache()
def executor() -> ThreadPoolExecutor:
    THREADS = int(os.environ.get("SCORE_THREADS", 16))
    return ThreadPoolExecutor(THREADS)


def do_map(fn, *iterables: Iterable[Any]):

    thread_count = int(os.environ.get("SCORE_THREADS", 16))
    if thread_count <= 1:
        return map(fn, *iterables)
    return executor().map(fn, *iterables)
