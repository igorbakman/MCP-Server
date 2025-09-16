import csv
from pathlib import Path
from typing import Dict, List, Tuple, Optional

DATA_DIR = Path(__file__).resolve().parent / "data"


def _find_csv(basename: str) -> Optional[Path]:
    exact = DATA_DIR / f"{basename}.csv"
    if exact.exists():
        return exact
    for p in DATA_DIR.iterdir():
        if p.is_file() and p.suffix.lower() == ".csv" and p.name.lower().startswith(basename.lower()):
            return p
    return None


def _normalize_author(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    s = raw.strip()
    if s.lower().startswith("by "):
        s = s[3:].strip()
    return s or None


def _split_genres(raw: Optional[str]) -> List[str]:
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def _to_int_or_none(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    v = value.strip()
    if not v:
        return None
    try:
        return int(float(v))
    except Exception:
        return None


def _to_float_or_none(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    v = value.strip().replace(",", "")
    if not v:
        return None
    try:
        return float(v)
    except Exception:
        return None


def load_books() -> List[dict]:
    path = _find_csv("BooksDatasetClean")
    if path is None:
        raise FileNotFoundError("Books dataset CSV not found in app/data/. Expected e.g. BooksDatasetClean.csv")
    items: List[dict] = []
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            title = (row.get("Title") or "").strip()
            author = _normalize_author(row.get("Authors"))
            description = (row.get("Description") or "").strip() or None
            genres = _split_genres(row.get("Category"))
            publisher = (row.get("Publisher") or "").strip() or None
            year = _to_int_or_none(row.get("Publish Date (Year)"))
            price = _to_float_or_none(row.get("Price Starting With ($)"))
            items.append({
                "id": idx + 1,
                "title": title,
                "author": author,
                "description": description,
                "genres": genres,
                "publisher": publisher,
                "year": year,
                "price_usd": price,
            })
    return items


def load_rates() -> Dict[Tuple[str, str], float]:
    path = _find_csv("exchange_rates_dataset")
    if path is None:
        raise FileNotFoundError(
            "Exchange rates dataset CSV not found in app/data/. Expected e.g. exchange_rates_dataset.csv")
    rates: Dict[Tuple[str, str], float] = {}
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            base = (row.get("base_currency") or "").upper().strip()
            tgt = (row.get("target_currency") or "").upper().strip()
            rate = _to_float_or_none(row.get("rate"))
            if not base or not tgt or rate is None:
                continue
            rates[(base, tgt)] = float(rate)
    return rates
