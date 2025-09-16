import json

from fastapi import FastAPI
from starlette.responses import JSONResponse

from .routers import books, exchange


class PrettyJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(content, ensure_ascii=False, indent=2).encode("utf-8")


app = FastAPI(
    title="MCP Assignment API",
    version="2.0.0",
    default_response_class=PrettyJSONResponse
)


@app.get("/resources")
def resources():
    return {
        "resources": [
            {
                "name": "books",
                "type": "static",
                "endpoints": ["/books", "/books/{id}"],
                "filters": [
                    "q", "title_contains", "author", "genre",
                    "year", "min_price", "max_price",
                    "sort_by", "order", "page", "per_page"
                ]
            },
            {
                "name": "exchange",
                "type": "dynamic",
                "endpoints": ["/exchange"],
                "params": ["from", "to", "amount"]
            }
        ]
    }


app.include_router(books.router)
app.include_router(exchange.router)


@app.get("/healthz")
def health():
    return {"ok": True}
