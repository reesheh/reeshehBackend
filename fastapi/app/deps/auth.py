from fastapi import Depends, HTTPException, Request, status
from jose import jwt
import httpx, time

from app.core.config import settings

_JWKS = None
_NEXT_REFRESH = 0

async def _get_jwks():
    global _JWKS, _NEXT_REFRESH
    now = time.time()
    if not _JWKS or now >= _NEXT_REFRESH:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(settings.SUPABASE_JWKS_URL)
            r.raise_for_status()
            _JWKS = r.json()
            _NEXT_REFRESH = now + 3600
    return _JWKS

def _match_key(jwks, kid):
    for k in jwks.get("keys", []):
        if k.get("kid") == kid:
            return k
    return None

async def get_current_user_id(request: Request) -> str:
    auth = request.headers.get("authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    token = auth.split(" ", 1)[1]
    unverified = jwt.get_unverified_header(token)
    jwks = await _get_jwks()
    key = _match_key(jwks, unverified.get("kid"))
    if not key:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=[key.get("alg", "RS256")],
            audience=settings.JWT_EXPECTED_AUD,
            issuer=settings.JWT_EXPECTED_ISS,
            options={"verify_at_hash": False},
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="No subject")
    return sub  # Supabase user id
