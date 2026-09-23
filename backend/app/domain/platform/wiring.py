"""Platform capability wiring (see app/registry.py). Event contracts are hand-written in contracts/events/platform/."""

PERMISSIONS = {
    "OPERATOR": ["operators:read", "machines:read", "sites:read"],
    "SUPERVISOR_ADMIN": ["operators:read", "operators:write", "machines:read", "machines:write", "sites:read",
                         "sites:write", "zones:write", "audit:read"],
}
