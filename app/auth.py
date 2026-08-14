from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from config import settings

api_key_header = APIKeyHeader(name=settings.API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key_header: str = Security(api_key_header)):
    """Enforces API Key authorization for protected API routes."""
    if api_key_header == settings.API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing X-API-Key header",
    )