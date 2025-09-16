from functools import lru_cache
from typing import List, Dict, Tuple

from .data_loader import load_books, load_rates


@lru_cache(maxsize=1)
def _books_cache() -> tuple:
    return tuple(load_books())


@lru_cache(maxsize=1)
def _rates_cache() -> Dict[Tuple[str, str], float]:
    return load_rates()


def get_books() -> List[dict]:
    return list(_books_cache())


def get_rates() -> Dict[Tuple[str, str], float]:
    return _rates_cache()
