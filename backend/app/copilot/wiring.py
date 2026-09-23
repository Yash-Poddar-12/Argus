"""Copilot component wiring (see app/registry.py): generates contracts/tools/<name>.json from TOOL_SPECS."""

from __future__ import annotations

from pydantic.json_schema import models_json_schema

from app.copilot.tools.registry import TOOL_SPECS


def contract_documents() -> dict[str, dict]:
    docs: dict[str, dict] = {}
    for name, spec in TOOL_SPECS.items():
        keys, defs = models_json_schema([(spec["input"], "validation"), (spec["output"], "validation")],
                                        ref_template="#/$defs/{model}")
        docs[f"tools/{name}.json"] = {
            "title": name,
            "description": spec["description"],
            "x-tool": {"name": name, "version": "1.0", "owner": spec["owner"],
                       "permissions": ["OPERATOR:self", "SUPERVISOR_ADMIN:site"], "safety_critical": False,
                       "latency_budget_ms": 500},
            "type": "object",
            "required": ["input", "output"],
            "properties": {"input": keys[(spec["input"], "validation")], "output": keys[(spec["output"], "validation")]},
            **defs,
        }
    return docs
