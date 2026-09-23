#!/usr/bin/env python3
"""Contract tooling (M00). Run with the project env: ``uv run python scripts/contracts.py <cmd>``.

  check           Validate every JSON Schema under contracts/, every example against its schema,
                  and every OpenAPI file's basic shape. Non-zero exit on any problem.
  export          Regenerate contracts/openapi/<module>.yaml for every backend module that has a
                  router, plus any JSON documents a module generates from its models via
                  ``contract_documents()`` in module.py (schemas, event payloads, tool schemas).
  export --check  Fail if the committed OpenAPI files differ from what the code generates (CI).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
CONTRACTS = ROOT / "contracts"


def _load(path: Path):
    text = path.read_text(encoding="utf-8")
    return yaml.safe_load(text) if path.suffix in {".yaml", ".yml"} else json.loads(text)


def cmd_check(_: argparse.Namespace) -> int:
    from backend.core.contracts import validate_json

    problems: list[str] = []
    schemas = [p for p in CONTRACTS.rglob("*.json") if "examples" not in p.parts]
    for path in schemas:
        rel = path.relative_to(ROOT).as_posix()
        try:
            schema = _load(path)
            Draft202012Validator.check_schema(schema)
        except Exception as exc:  # noqa: BLE001
            problems.append(f"{rel}: invalid schema: {exc}")
            continue
        expected_id = "https://argus.local/" + path.relative_to(ROOT).as_posix()
        if schema.get("$id") != expected_id:
            problems.append(f"{rel}: $id must be {expected_id}")
        parts = path.relative_to(CONTRACTS).parts
        needs_example = parts[0] in {"events", "tools", "ml"} and "ws" not in parts and not path.name.startswith("_")
        if needs_example:
            example = path.parent / "examples" / (path.stem + ".example.json")
            if not example.exists():
                problems.append(f"{rel}: missing example {example.relative_to(ROOT).as_posix()}")

    for example in CONTRACTS.rglob("examples/*.example.json"):
        schema_path = example.parent.parent / example.name.replace(".example.json", ".json")
        rel = example.relative_to(ROOT).as_posix()
        if not schema_path.exists():
            problems.append(f"{rel}: no matching schema {schema_path.name}")
            continue
        try:
            validate_json(schema_path, _load(example))
        except Exception as exc:  # noqa: BLE001
            problems.append(f"{rel}: {exc}")

    for spec_path in sorted((CONTRACTS / "openapi").glob("*.yaml")):
        rel = spec_path.relative_to(ROOT).as_posix()
        try:
            spec = _load(spec_path)
        except Exception as exc:  # noqa: BLE001
            problems.append(f"{rel}: YAML error: {exc}")
            continue
        for key in ("openapi", "info", "paths"):
            if key not in (spec or {}):
                problems.append(f"{rel}: missing '{key}'")
        if spec and not str(spec.get("openapi", "")).startswith("3."):
            problems.append(f"{rel}: openapi must be 3.x")

    n_ex = len(list(CONTRACTS.rglob("examples/*.example.json")))
    n_api = len(list((CONTRACTS / "openapi").glob("*.yaml")))
    print(f"contracts: {len(schemas)} schemas, {n_ex} examples, {n_api} OpenAPI files")
    for p in problems:
        print(f"  FAIL {p}")
    print("OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


def _refs(node, found: set[str]) -> None:
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
            found.add(ref.rsplit("/", 1)[1])
        for v in node.values():
            _refs(v, found)
    elif isinstance(node, list):
        for v in node:
            _refs(v, found)


def generate_specs() -> dict[Path, str]:
    os.environ.setdefault("DISABLED_MODULES", "")
    from backend.core.app import create_app
    from backend.core.config import Settings

    app = create_app(Settings(database_url="sqlite+aiosqlite:///:memory:", log_json=False))
    full = app.openapi()
    module_paths: dict[str, set[str]] = app.state.module_paths
    owned = set().union(*module_paths.values()) if module_paths else set()
    from backend.core.registry import discover

    files: dict[Path, str] = {}
    for m in discover():
        if m.name not in module_paths:
            continue
        paths = {p: v for p, v in full["paths"].items() if p in module_paths[m.name]}
        if m.module_id == "M00":  # ops endpoints belong to M00
            paths.update({p: v for p, v in full["paths"].items() if p not in owned})
        needed: set[str] = set()
        _refs(paths, needed)
        schemas = full.get("components", {}).get("schemas", {})
        while True:  # transitive closure of referenced component schemas
            before = len(needed)
            _refs({k: schemas[k] for k in needed if k in schemas}, needed)
            if len(needed) == before:
                break
        spec = {
            "openapi": full["openapi"],
            "info": {"title": f"{m.module_id} {m.name} API", "version": getattr(m.module, "API_VERSION", "1.0.0"),
                     "description": "GENERATED by scripts/contracts.py export from backend code. Do not hand-edit."},
            "paths": dict(sorted(paths.items())),
            "components": {"schemas": {k: schemas[k] for k in sorted(needed) if k in schemas}},
        }
        if any("HTTPBearer" in json.dumps(v) for v in paths.values()):
            spec["components"]["securitySchemes"] = full["components"]["securitySchemes"]
        name = getattr(m.module, "OPENAPI_FILE", m.name.replace("_", "-") + ".yaml")
        files[CONTRACTS / "openapi" / name] = yaml.safe_dump(spec, sort_keys=False, allow_unicode=True, width=120)
    for m in discover():
        producer = getattr(m.module, "contract_documents", None)
        if producer is None:
            continue
        for rel, doc in producer().items():
            full_doc = {"$schema": "https://json-schema.org/draft/2020-12/schema",
                        "$id": f"https://argus.local/contracts/{rel}",
                        "$comment": f"GENERATED from {m.name} models by scripts/contracts.py export. Do not hand-edit.",
                        **{k: v for k, v in doc.items() if k not in ("$schema", "$id")}}
            files[CONTRACTS / rel] = json.dumps(full_doc, indent=2, ensure_ascii=False) + "\n"
    return files


def cmd_export(args: argparse.Namespace) -> int:
    files = generate_specs()
    drift = []
    for path, text in files.items():
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current != text:
            drift.append(path)
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(text.encode("utf-8"))
    for path in drift:
        print(("DRIFT " if args.check else "wrote ") + path.relative_to(ROOT).as_posix())
    if args.check and drift:
        print("Generated contracts are out of date with the code. Run: uv run python scripts/contracts.py export")
        return 1
    print(f"{len(files)} generated contract file(s) {'checked' if args.check else 'up to date' if not drift else 'exported'}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check").set_defaults(func=cmd_check)
    ex = sub.add_parser("export")
    ex.add_argument("--check", action="store_true")
    ex.set_defaults(func=cmd_export)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
