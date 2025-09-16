from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query, Request, Depends

from ..auth import get_api_key
from ..deps import get_books
from ..models import (
    Price, Publishing, ItemLinks, BookOut,
    PaginationMeta, ListLinks, BooksEnvelope
)

router = APIRouter(tags=["books"], dependencies=[Depends(get_api_key)])


def _contains(hay: Optional[str], needle: str) -> bool:
    return bool(hay) and (needle in hay.lower())


@router.get("/books", response_model=BooksEnvelope, response_model_exclude_none=True)
def list_books(
        request: Request,
        q: Optional[str] = Query(None, description="Search in title/author/description"),
        title_contains: Optional[str] = Query(None, description="Partial title match"),
        author: Optional[str] = Query(None, description="Exact author"),
        genre: Optional[str] = Query(None, description="Exact genre"),
        year: Optional[int] = Query(None, description="Publish year"),
        min_price: Optional[float] = Query(None, ge=0),
        max_price: Optional[float] = Query(None, ge=0),
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=200),
        sort_by: Optional[str] = Query(None, pattern="^(title|year|price)$"),
        order: str = Query("asc", pattern="^(asc|desc)$"),
        books: List[dict] = Depends(get_books),
):
    if not books:
        raise HTTPException(status_code=500, detail="Books dataset not loaded. Put CSV in app/data/ and restart.")

    items = books

    if q:
        ql = q.lower()
        items = [b for b in items if _contains(b.get("title"), ql)
                 or _contains(b.get("author"), ql)
                 or _contains(b.get("description"), ql)]
    if title_contains:
        tl = title_contains.lower()
        items = [b for b in items if _contains(b.get("title"), tl)]
    if author:
        items = [b for b in items if (b.get("author") or "").lower() == author.lower()]
    if genre:
        items = [b for b in items if any(g.lower() == genre.lower() for g in b.get("genres", []))]
    if year is not None:
        items = [b for b in items if b.get("year") == year]
    if min_price is not None:
        items = [b for b in items if (b.get("price_usd") is not None and b["price_usd"] >= min_price)]
    if max_price is not None:
        items = [b for b in items if (b.get("price_usd") is not None and b["price_usd"] <= max_price)]

    if sort_by:
        reverse = (order == "desc")
        if sort_by == "title":
            key_fn = lambda b: (b.get("title") or "").lower()
        elif sort_by == "year":
            key_fn = lambda b: b.get("year") or 0
        else:  # price
            key_fn = lambda b: b.get("price_usd") if b.get("price_usd") is not None else float("inf")
        items = sorted(items, key=key_fn, reverse=reverse)

    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    page_items = items[start:end]

    def to_out(b: dict) -> BookOut:
        return BookOut(
            id=b["id"],
            title=b["title"],
            author=b.get("author"),
            description=b.get("description"),
            genres=b.get("genres", []),
            price=Price(amount=b["price_usd"], currency="USD") if b.get("price_usd") is not None else None,
            publishing=Publishing(publisher=b.get("publisher"), year=b.get("year")),
            links=ItemLinks(self=str(request.url_for("get_book", book_id=b["id"])))
        )

    data: List[BookOut] = [to_out(b) for b in page_items]

    total_pages = (total + per_page - 1) // per_page
    has_next = end < total
    has_prev = page > 1

    url = request.url
    self_url = str(url)
    next_url = str(
        url.replace_query_params(**{**dict(request.query_params), "page": str(page + 1)})) if has_next else None
    prev_url = str(
        url.replace_query_params(**{**dict(request.query_params), "page": str(page - 1)})) if has_prev else None

    return BooksEnvelope(
        data=data,
        meta=PaginationMeta(total=total, page=page, perPage=per_page,
                            totalPages=total_pages, hasNext=has_next, hasPrev=has_prev),
        links=ListLinks(self=self_url, next=next_url, prev=prev_url)
    )


@router.get("/books/{book_id}", name="get_book", response_model=BookOut, response_model_exclude_none=True)
def get_book(request: Request, book_id: int, books: List[dict] = Depends(get_books)):
    if not books:
        raise HTTPException(status_code=500, detail="Books dataset not loaded. Put CSV in app/data/ and restart.")
    if 1 <= book_id <= len(books):
        b = books[book_id - 1]
        return BookOut(
            id=b["id"],
            title=b["title"],
            author=b.get("author"),
            description=b.get("description"),
            genres=b.get("genres", []),
            price=Price(amount=b["price_usd"], currency="USD") if b.get("price_usd") is not None else None,
            publishing=Publishing(publisher=b.get("publisher"), year=b.get("year")),
            links=ItemLinks(self=str(request.url))
        )
    raise HTTPException(status_code=404, detail="Book not found")
