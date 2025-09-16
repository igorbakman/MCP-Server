import pytest
from fastapi.testclient import TestClient

from app.auth import get_api_key
from app.deps import get_books, get_rates
from app.main import app


@pytest.fixture(autouse=True)
def override_dependencies():
    books = [
        {
            "id": 1, "title": "Alpha History", "author": "Jane Doe",
            "description": "A short intro", "genres": ["History"],
            "publisher": "Acme", "year": 1997, "price_usd": 10.0
        },
        {
            "id": 2, "title": "Beta Science", "author": "John Roe",
            "description": "Science basics", "genres": ["Science"],
            "publisher": "Acme", "year": 2001, "price_usd": 15.5
        },
        {
            "id": 3, "title": "Gamma History", "author": "Jane Doe",
            "description": "Another history", "genres": ["History", "War"],
            "publisher": "Books&Co", "year": 1993, "price_usd": 7.25
        },
    ]
    rates = {
        ("USD", "EUR"): 0.9,
        ("USD", "GBP"): 0.8,
        ("USD", "USD"): 1.0,
    }

    app.dependency_overrides[get_books] = lambda: books
    app.dependency_overrides[get_rates] = lambda: rates
    app.dependency_overrides[get_api_key] = lambda: "test-key"  # bypass auth in tests
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)
