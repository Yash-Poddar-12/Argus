"""Role-based access control: Identity -> Role -> Permissions -> Site scope -> Resource (master §3.4).

Core knows only the two product roles. Each domain registers its own permission strings through
``PERMISSIONS`` in its ``wiring.py`` (merged at startup), so core never hard-codes business permissions.
Code checks permissions (``require_permission("tasks:assign")``) and scope, never role names.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from app.core.exceptions import Forbidden

Role = Literal["OPERATOR", "SUPERVISOR_ADMIN"]
ROLES: tuple[Role, ...] = ("OPERATOR", "SUPERVISOR_ADMIN")

ROLE_PERMISSIONS: dict[str, set[str]] = {"OPERATOR": {"self:read"}, "SUPERVISOR_ADMIN": {"self:read"}}


def register_permissions(extra: dict[str, list[str]]) -> None:
    for role, perms in extra.items():
        if role not in ROLES:
            raise ValueError(f"Unknown role '{role}' (the product has exactly {ROLES})")
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
