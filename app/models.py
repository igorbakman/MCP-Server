from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


# -------- camelCase helper --------
def to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


class CamelModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


# -------- exchange response --------
class FxResponse(BaseModel):
    converted: float
    rate_used: float
    via: List[str]


# -------- books (human-readable) ----
class Price(CamelModel):
    amount: float
    currency: str = "USD"


class Publishing(CamelModel):
    publisher: Optional[str] = None
    year: Optional[int] = None


class ItemLinks(CamelModel):
    self: str


class BookOut(CamelModel):
    id: int
    title: str
    author: Optional[str] = None
    description: Optional[str] = None
    genres: List[str] = []
    price: Optional[Price] = None
    publishing: Publishing
    links: ItemLinks


class PaginationMeta(CamelModel):
    total: int
    page: int
    per_page: int = Field(alias="perPage")
    total_pages: int = Field(alias="totalPages")
    has_next: bool = Field(alias="hasNext")
    has_prev: bool = Field(alias="hasPrev")


class ListLinks(CamelModel):
    self: str
    next: Optional[str] = None
    prev: Optional[str] = None


class BooksEnvelope(CamelModel):
    data: List[BookOut]
    meta: PaginationMeta
    links: ListLinks
