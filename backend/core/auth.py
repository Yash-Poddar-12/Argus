"""Authentication, RBAC and site scope (M00).

Identity -> Role -> Permissions -> Site scope -> Resource (master §3.4).
Modules check permissions with ``require_permission("tasks:assign")`` and scope with
``principal.ensure_site(...)`` / ``principal.ensure_operator(...)``, never with role names.
Modules add permissions through ``permissions`` in their ``module.py`` (merged by the registry).
"""

from __future__ import annotations

import hashlib
import hmac
import os
from datetime import timedelta
from typing import Literal

import jwt
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from backend.core.config import get_settings
from backend.core.db import utcnow
from backend.core.errors import Forbidden, Unauthorized

Role = Literal["OPERATOR", "SUPERVISOR_ADMIN"]
ROLES: tuple[Role, ...] = ("OPERATOR", "SUPERVISOR_ADMIN")

# Baseline permissions owned by M00. Modules extend via module.py `permissions`.
ROLE_PERMISSIONS: dict[str, set[str]] = {
    "OPERATOR": {"self:read", "operators:read", "machines:read", "sites:read"},
    "SUPERVISOR_ADMIN": {
        "self:read", "operators:read", "operators:write", "machines:read", "machines:write",
        "sites:read", "sites:write", "zones:write", "audit:read",
    },
}


def register_permissions(extra: dict[str, list[str]]) -> None:
    for role, perms in extra.items():
        ROLE_PERMISSIONS.setdefault(role, set()).update(perms)


class Principal(BaseModel):
    user_id: str
    username: str
    role: Role
    operator_id: str | None = None
    site_ids: list[str] = []

    @property
    def permissions(self) -> set[str]:
        return ROLE_PERMISSIONS.get(self.role, set())

    def has(self, permission: str) -> bool:
        return permission in self.permissions

    def ensure_site(self, site_id: str | None) -> None:
        if site_id is not None and site_id not in self.site_ids:
            raise Forbidden(f"No access to site '{site_id}'")

    def ensure_operator(self, operator_id: str, site_id: str | None = None) -> None:
        """Operators may only access themselves; supervisors any operator in their sites."""
        if self.role == "OPERATOR":
            if self.operator_id != operator_id:
                raise Forbidden("Operators can only access their own data")
        else:
            self.ensure_site(site_id)


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
