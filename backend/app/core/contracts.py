"""Runtime access to machine-readable contracts in ``contracts/`` (M00).

Used for producer-conformance checks: in tests (``validate_events=True``) every published
event payload is validated against ``contracts/events/<area>/<event_type>.v<major>.json``.
The contracts directory is the repo's ``contracts/`` (override with ``ARGUS_CONTRACTS_DIR``, e.g. in Docker).
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[3]  # backend/app/core/contracts.py -> repo root
CONTRACTS = Path(os.environ.get("ARGUS_CONTRACTS_DIR") or ROOT / "contracts").resolve()


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
    hits = sorted(CONTRACTS.glob(f"events/*/{event_type}.v{major}.json"))
    return hits[0] if hits else None


@lru_cache
def _validator(path: Path) -> Draft202012Validator:
    schema = json.loads(path.read_text(encoding="utf-8"))
    return Draft202012Validator(schema, registry=_registry())


def validate_json(path: Path, instance: object) -> None:
    errors = sorted(_validator(path).iter_errors(instance), key=lambda e: list(e.path))
    if errors:
        msg = "; ".join(f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors[:5])
        raise ContractError(f"{path.relative_to(CONTRACTS.parent)}: {msg}")


def validate_event_payload(event_type: str, version: str, payload: dict) -> None:
    path = event_schema_path(event_type, version)
    if path is None:
        raise ContractError(f"No contract for event '{event_type}' v{version} under contracts/events/*/")
    validate_json(path, payload)


def event_payload_schema(event_type: str, model, producer: str) -> dict:
    """JSON Schema for an event payload generated from its pydantic model (used by wiring.contract_documents)."""
    schema = model.model_json_schema()
    schema["description"] = f"Payload of '{event_type}' (producer: {producer}). " + (schema.get("description") or "")
    return schema


def event_documents(area: str, payloads: dict) -> dict[str, dict]:
    """contract_documents() entries for all events a capability produces: contracts/events/<area>/<type>.v1.json."""
    return {f"events/{area}/{event_type}.v1.json": event_payload_schema(event_type, model, area)
            for event_type, model in payloads.items()}
