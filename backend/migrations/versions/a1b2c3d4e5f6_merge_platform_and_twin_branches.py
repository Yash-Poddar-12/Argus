"""Merge the historical per-module branches (m00_platform, m01_twin) into a single linear history.

After this revision every new migration is linear: ``alembic revision --autogenerate -m "..."`` then
``alembic upgrade head``. The original revisions and their branch labels are kept untouched, so databases
created before the repository restructure upgrade without changes.

Revision ID: a1b2c3d4e5f6
Revises: m00_0001, 6a49290df5f0
Create Date: 2026-09-23
"""
from collections.abc import Sequence

revision: str = "a1b2c3d4e5f6"
down_revision: str | Sequence[str] | None = ("m00_0001", "6a49290df5f0")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
