from app.models import BooksEnvelope, BookOut


def test_books_envelope_structure(client):
    r = client.get("/books?per_page=2")
    assert r.status_code == 200
    body = r.json()
    assert set(body.keys()) == {"data", "meta", "links"}
    assert set(body["meta"].keys()) == {"total", "page", "perPage", "totalPages", "hasNext", "hasPrev"}
    BooksEnvelope.model_validate(body)


def test_books_filter_title_contains(client):
    r = client.get("/books", params={"title_contains": "alpha"})
    assert r.status_code == 200
    data = r.json()["data"]
    assert any("Alpha" in item["title"] for item in data)


def test_books_filter_by_genre(client):
    r = client.get("/books", params={"genre": "History"})
    assert r.status_code == 200
    data = r.json()["data"]
    assert len(data) >= 1
    assert all("History" in item["genres"] for item in data)


def test_books_author_exact_and_pagination(client):
    r = client.get("/books", params={"author": "Jane Doe", "per_page": 1, "page": 1, "sort_by": "year", "order": "asc"})
    assert r.status_code == 200
    body = r.json()
    assert body["meta"]["perPage"] == 1
    assert body["meta"]["page"] == 1
    assert body["meta"]["hasNext"] in (True, False)


def test_get_book_happy_and_404(client):
    ok = client.get("/books/1")
    assert ok.status_code == 200
    BookOut.model_validate(ok.json())

    not_found = client.get("/books/999")
    assert not_found.status_code == 404
