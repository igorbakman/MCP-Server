# MCP Assignment API — FastAPI 🍯

A tiny, comfy REST API that serves **Books** from a CSV and a simple **Exchange** endpoint. It’s built for quick review: clean JSON, interactive docs, sensible pagination, optional API-key auth, and a one-file Docker image.

---

## ✨ Features

* **CSV-only** data loading (no DB required)
* **Human-readable JSON** (`data` + `meta` + `links`)
* **Partial title search** (`title_contains`) and full-text-ish `q`
* **Pagination** (page, perPage, totalPages, hasNext/Prev + links)
* **API key auth** for protected routes (`X-API-Key`)
* **Interactive docs** at `/docs` and `/redoc`
* **Dockerized** for zero-friction setup

---

## 🗂 Project layout

```
app/
  __init__.py
  main.py            # FastAPI app, routes wired
  auth.py            # X-API-Key header auth
  deps.py            # dependency providers (cached)
  models.py          # Pydantic response models (camelCase)
  data_loader.py     # CSV readers (Books + FX rates)
  routers/
    __init__.py
    books.py         # /books, /books/{id}
    exchange.py      # /exchange
  data/
    BooksDatasetClean.csv
    exchange_rates_dataset.csv
tests/
  conftest.py
  test_books.py
  test_exchange.py
requirements.txt
Dockerfile
```

---

## 🚀 Quickstart

### 1) Install & run locally

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# (optional) enable auth:
export API_KEY=supersecret123
uvicorn app.main:app --reload --port 8000
```

Open:

* Swagger UI → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* ReDoc → [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### 2) Run with Docker

```bash
docker build -t mcp-api .
docker run --rm -p 8000:8000 \
  -e API_KEY=supersecret123 \
  -v "$PWD/app/data:/app/app/data:ro" \
  mcp-api
```

> Don’t have Docker? On macOS: `brew install docker colima && colima start`.

---

## 🔐 Authentication

* Protected routes: `/books`, `/books/{id}`, `/exchange`
* Header: `X-API-Key: <your-key>`
* Server key: environment variable `API_KEY`

  * If **unset**, auth is **disabled** (handy for local dev)

**curl example:**

```bash
curl -H "X-API-Key: supersecret123" \
  "http://127.0.0.1:8000/books?title_contains=war&per_page=5"
```

In Swagger UI: click **Authorize** and paste the API key.

---

## 📚 Endpoints

### `GET /resources` (open)

Lists available resources and parameters.

### `GET /books` (protected)

Query params:

* Search: `q` (title/author/description contains), **`title_contains`** (title only)
* Filters: `author`, `genre`, `year`, `min_price`, `max_price`
* Sorting: `sort_by=title|year|price`, `order=asc|desc`
* Pagination: `page` (default 1), `per_page` (default 20, max 200)

Response shape:

```json
{
  "data": [{ ...BookOut }],
  "meta": {
    "total": 314,
    "page": 2,
    "perPage": 20,
    "totalPages": 16,
    "hasNext": true,
    "hasPrev": true
  },
  "links": {
    "self": "http://127.0.0.1:8000/books?genre=History&page=2",
    "next": "http://127.0.0.1:8000/books?genre=History&page=3",
    "prev": "http://127.0.0.1:8000/books?genre=History&page=1"
  }
}
```

Each `BookOut`:

```json
{
  "id": 21,
  "title": "The Roman Empire",
  "author": "Jane Doe",
  "description": "…",
  "genres": ["History"],
  "price": { "amount": 12.99, "currency": "USD" },
  "publishing": { "publisher": "Acme", "year": 1997 },
  "links": { "self": "http://127.0.0.1:8000/books/21" }
}
```

### `GET /books/{id}` (protected)

Returns a single `BookOut` or `404` if not found.

### `GET /exchange?from=&to=&amount=` (protected)

* Uses direct pair or crosses via USD:

  * `rate(A→B) = rate(USD→B) / rate(USD→A)` when needed
* Response:

```json
{ "converted": 9.0, "rate_used": 0.9, "via": ["USD"] }
```

### `GET /healthz` (open)

Simple health check.

---

## 🧪 Tests

```bash
pip install pytest
pytest -q
```

* Tests override data via **dependency injection** (no CSV needed)
* Coverage includes:

  * `/books` envelope, filters, sorting, pagination, links, 404
  * `/exchange` direct + cross rates, invalid currency

---

## 🧩 CSVs & assumptions

* IDs are **1-based row indices** in `BooksDatasetClean.csv`.
* `genres` split from `Category` on commas.
* `price_usd` parsed from `Price Starting With ($)`; missing values omitted.
* FX dataset is assumed **USD-based**; crossed pairs go via USD.

> Want stable IDs even if CSV order changes? Switch to a hash of `(title|author|year)`—happy to show how.

---

## 🛠 Troubleshooting

* **`ModuleNotFoundError: No module named 'app'`**
  Run from the **project root**:
  `uvicorn app.main:app --reload`
  In PyCharm Run/Debug, set **Working directory** to the project root.
* **401 Unauthorized**
  Ensure server has `API_KEY` set and your request includes header `X-API-Key`.
* **No data loaded**
  Place `BooksDatasetClean.csv` and `exchange_rates_dataset.csv` under `app/data/` and restart.

---

## 📦 Tech stack

* Python 3.11 · FastAPI · Uvicorn
* Pydantic (camelCase models, clean schema)
* pytest (tests), Docker (runtime)

---

