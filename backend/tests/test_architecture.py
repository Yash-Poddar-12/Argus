"""Architecture rules (docs/architecture/REPOSITORY_STRUCTURE.md §4). Static import analysis: no app startup needed."""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
APP = REPO / "backend" / "app"


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            found.add(node.module)
            found.update(f"{node.module}.{a.name}" for a in node.names)
        elif isinstance(node, ast.Import):
            found.update(a.name for a in node.names)
    return found


def _module_files(package: str) -> list[Path]:
    return sorted((APP / package.replace(".", "/")).rglob("*.py")) if package else sorted(APP.rglob("*.py"))


RULES = [
    # (layer package, forbidden import prefixes, why)
    ("core", ("app.domain", "app.api", "app.copilot", "app.iot", "app.registry", "app.main", "app.seed"),
     "core is technical infrastructure and must not know business capabilities"),
    ("domain", ("app.api", "app.copilot", "app.iot", "app.main"),
     "domain logic must not depend on delivery (API), AI agents or device code"),
    ("api", ("sqlalchemy.select", "sqlalchemy.orm", "app.core.database"),
     "routes stay thin: queries belong in domain services"),
    ("copilot", ("sqlalchemy", "app.core.database", "app.api"),
     "the Copilot reaches data only through domain services (never the database or raw tables)"),
    ("iot", ("app.api",), "device/simulator code feeds the domain through services and events, not HTTP routes"),
]


@pytest.mark.parametrize("layer,forbidden,why", RULES, ids=[r[0] for r in RULES])
def test_layer_dependencies(layer, forbidden, why):
    violations = []
    for f in _module_files(layer):
        for imp in _imports(f):
            if any(imp == bad or imp.startswith(bad + ".") for bad in forbidden):
                violations.append(f"{f.relative_to(REPO).as_posix()} imports {imp}")
    assert not violations, f"{why}:\n" + "\n".join(violations)


def test_api_and_copilot_never_import_domain_models():
    pattern = re.compile(r"^app\.domain\.\w+\.models\b")
    violations = [f"{f.relative_to(REPO).as_posix()} imports {imp}"
                  for layer in ("api", "copilot") for f in _module_files(layer)
                  for imp in _imports(f) if pattern.match(imp)]
    assert not violations, "only the owning domain touches its tables:\n" + "\n".join(violations)


def test_domains_do_not_write_other_domains_tables():
    """Cross-domain model imports are read-only exceptions, listed explicitly (the twin is the context read model)."""
    allowed_reads = {
        "twin": {"tasks", "telemetry", "environment"},       # twin fuses context from these (read-only)
        "tasks": {"telemetry"},                               # task summary reads telemetry history
        "telemetry": set(),
    }
    violations = []
    for pkg in (APP / "domain").iterdir():
        if not pkg.is_dir() or pkg.name.startswith("_"):
            continue
        for f in pkg.rglob("*.py"):
            for imp in _imports(f):
                m = re.match(r"^app\.domain\.(\w+)\.models\b", imp)
                if m and m.group(1) != pkg.name and m.group(1) not in allowed_reads.get(pkg.name, set()):
                    violations.append(f"{f.relative_to(REPO).as_posix()} imports {imp}")
    assert not violations, "use the owning domain's service instead:\n" + "\n".join(violations)


def test_top_level_layout_is_intentional():
    allowed = {"backend", "frontend", "ml", "models", "contracts", "infra", "docs", "scripts", "tests", "edge", ".github"}
    ignored = {".git", ".venv", ".data", ".pytest_cache", ".ruff_cache", ".idea", ".vscode", "node_modules", "__pycache__"}
    dirs = {p.name for p in REPO.iterdir() if p.is_dir() and p.name not in ignored}
    unexpected = dirs - allowed
    assert not unexpected, (f"new top-level folder(s) {sorted(unexpected)}: add code inside an existing area, or record "
                            "an ADR and extend this list (docs/architecture/REPOSITORY_STRUCTURE.md §1)")


def test_no_phase_numbered_code_or_contract_folders():
    """M00–M11 are workstreams (planning), not code boundaries."""
    phase = re.compile(r"^m\d\d([_-]|$)", re.I)
    roots = [APP, REPO / "contracts", REPO / "frontend" / "src"]
    offenders = [p.relative_to(REPO).as_posix() for root in roots for p in root.rglob("*")
                 if p.is_dir() and phase.match(p.name)]
    assert not offenders, offenders


def test_no_empty_capability_packages():
    """Packages are created when real code lands, not as placeholders."""
    empty = [p.relative_to(REPO).as_posix() for p in APP.rglob("*") if p.is_dir() and p.name != "__pycache__"
             and not [f for f in p.rglob("*.py") if f.name != "__init__.py" and f.stat().st_size > 0]]
    assert not empty, empty
