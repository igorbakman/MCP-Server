import os

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY_NAME = "X-API-Key"
_api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def get_api_key(api_key: str | None = Security(_api_key_header)) -> str:
    """
    Simple API-key auth via header X-API-Key.
    If env var API_KEY is not set, auth is disabled (dev mode).
    """
    expected = os.getenv("API_KEY")
    if not expected:
        return "dev-mode-no-auth"
    if api_key == expected:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Invalid or missing API key in header {API_KEY_NAME}",
    )
