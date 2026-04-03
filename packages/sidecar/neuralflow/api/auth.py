import hashlib
import hmac
import secrets
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from neuralflow.logging_config import auth_logger as logger

# In-memory token store: token_hash -> {label, created_at}
# In production, persist to DB.
_tokens: dict[str, dict] = {}

# Shared secret used for HMAC signing
_SECRET = secrets.token_hex(32)

router = APIRouter(prefix="/api/auth")


class TokenRequest(BaseModel):
    label: str = "remote-token"


class TokenResponse(BaseModel):
    token: str
    label: str
    created_at: float


class TokenVerify(BaseModel):
    valid: bool
    label: str | None = None


@router.post("/token", response_model=TokenResponse)
async def generate_token(body: TokenRequest):
    """Generate a shared secret token for remote sidecar access."""
    raw_token = f"nf_{uuid.uuid4().hex}"
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    _tokens[token_hash] = {
        "label": body.label,
        "created_at": time.time(),
    }
    return TokenResponse(token=raw_token, label=body.label, created_at=time.time())


@router.post("/verify", response_model=TokenVerify)
async def verify_token(request: Request):
    """Verify the Authorization header token."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return TokenVerify(valid=False)
    raw_token = auth[7:]
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    info = _tokens.get(token_hash)
    if not info:
        return TokenVerify(valid=False)
    return TokenVerify(valid=True, label=info["label"])


@router.get("/tokens")
async def list_tokens():
    """List all active tokens (labels only, no secrets)."""
    return [
        {"label": info["label"], "created_at": info["created_at"]}
        for info in _tokens.values()
    ]


@router.delete("/tokens/{label}", status_code=204)
async def revoke_token(label: str):
    """Revoke all tokens with the given label."""
    to_remove = [h for h, info in _tokens.items() if info["label"] == label]
    for h in to_remove:
        del _tokens[h]


# ── Dependency for protected endpoints ────────────────────────────────────────

async def require_auth(request: Request) -> None:
    """FastAPI dependency that verifies the Bearer token on protected endpoints.

    Raises **401** when the token is missing or invalid.
    """
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        logger.warning("auth_failure: missing or malformed Authorization header from %s", request.client.host if request.client else "unknown")
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header.")
    raw_token = auth[7:]
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    info = _tokens.get(token_hash)
    if not info:
        logger.warning("auth_failure: invalid token from %s", request.client.host if request.client else "unknown")
        raise HTTPException(status_code=401, detail="Invalid authorization token.")
