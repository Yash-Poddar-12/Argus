"""Runtime access to machine-readable contracts in ``contracts/`` (M00).

Used for producer-conformance checks: in tests (``validate_events=True``) every published
event payload is validated against ``contracts/events/<mXX>/<event_type>.v<major>.json``.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = ROOT / "contracts"


class ContractError(Exception):
    pass


@lru_cache
def _registry() -> Registry:
    resources = []
    for path in CONTRACTS.rglob("*.json"):
        if "examples" in path.parts:
            continue
        schema = json.loads(path.read_text(encoding="utf-8"))
        uri = schema.get("$id") or path.resolve().as_uri()
        resources.append((uri, Resource.from_contents(schema)))
        resources.append((path.resolve().as_uri(), Resource.from_contents(schema)))
    return Registry().with_resources(resources)


@lru_cache
def event_schema_path(event_type: str, version: str) -> Path | None:
    major = version.split(".")[0]
    hits = sorted(CONTRACTS.glob(f"events/m*/{event_type}.v{major}.json"))
    return hits[0] if hits else None


@lru_cache
def _validator(path: Path) -> Draft202012Validator:
    schema = json.loads(path.read_text(encoding="utf-8"))
    return Draft202012Validator(schema, registry=_registry())


def validate_json(path: Path, instance: object) -> None:
    errors = sorted(_validator(path).iter_errors(instance), key=lambda e: list(e.path))
    if errors:
        msg = "; ".join(f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors[:5])
        raise ContractError(f"{path.relative_to(ROOT)}: {msg}")


def validate_event_payload(event_type: str, version: str, payload: dict) -> None:
    path = event_schema_path(event_type, version)
    if path is None:
        raise ContractError(f"No contract for event '{event_type}' v{version} under contracts/events/m*/")
    validate_json(path, payload)
