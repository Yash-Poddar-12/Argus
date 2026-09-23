"""Authentication: password hashing, JWT issue/verify, FastAPI principal dependencies."""

from __future__ import annotations

import hashlib
import hmac
import os
from datetime import timedelta

import jwt
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings
from app.core.database import utcnow
from app.core.exceptions import Forbidden, Unauthorized
from app.core.security.rbac import Principal

# ---- passwords (stdlib PBKDF2; no native deps) ----


def hash_password(password: str, *, iterations: int = 200_000) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, iterations, salt, digest = stored.split("$")
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(iterations))
        return hmac.compare_digest(candidate.hex(), digest)
    except ValueError:
        return False


# ---- tokens ----


def issue_token(p: Principal) -> tuple[str, int]:
    s = get_settings()
    ttl = s.jwt_ttl_minutes * 60
    claims = {
        "sub": p.user_id, "usr": p.username, "role": p.role, "op": p.operator_id, "sites": p.site_ids,
        "iat": utcnow(), "exp": utcnow() + timedelta(seconds=ttl),
    }
    return jwt.encode(claims, s.jwt_secret, algorithm="HS256"), ttl


def decode_token(token: str) -> Principal:
    try:
        c = jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise Unauthorized("Invalid or expired token") from exc
    return Principal(user_id=c["sub"], username=c["usr"], role=c["role"], operator_id=c.get("op"),
                     site_ids=c.get("sites", []))


_bearer = HTTPBearer(auto_error=False)


async def current_principal(
    request: Request, creds: HTTPAuthorizationCredentials | None = Depends(_bearer)
) -> Principal:
    if creds is None:
        raise Unauthorized()
    principal = decode_token(creds.credentials)
    request.state.principal = principal
    return principal


def require_permission(permission: str):
    async def _dep(principal: Principal = Depends(current_principal)) -> Principal:
        if not principal.has(permission):
            raise Forbidden(f"Missing permission '{permission}'")
        return principal

    return _dep
