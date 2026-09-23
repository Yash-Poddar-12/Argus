#!/usr/bin/env python3
"""Cross-platform task runner (M00). Works without make/bash (Windows friendly).

    python scripts/dev.py env                 create .env from infra/env/*.env.example (if missing)
    python scripts/dev.py api                 run backend in LITE mode (SQLite + in-memory bus), auto-seeded
    python scripts/dev.py web operator|admin  run a frontend app (needs Node; uses npx pnpm)
    python scripts/dev.py up | down           full stack via Docker Compose (base + every module file)
    python scripts/dev.py migrate             alembic upgrade heads
    python scripts/dev.py revision --module m01_twin -m "add x"   new migration on the module's branch
    python scripts/dev.py seed                demo data (glossary IDs) into the configured DB
    python scripts/dev.py sim [args...]       simulator CLI (M01), e.g. sim --scenario S1 --seed 42
    python scripts/dev.py test [module]       pytest (all, or backend/tests/<module>)
    python scripts/dev.py lint                ruff
    python scripts/dev.py contracts           validate contracts, export OpenAPI, regenerate API client
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PNPM = ["npx", "--yes", "pnpm@9"]


def run(cmd: list[str], env: dict | None = None, cwd: Path = ROOT) -> int:
    print("$", " ".join(cmd), flush=True)
    exe = shutil.which(cmd[0]) or cmd[0]
    return subprocess.call([exe, *cmd[1:]], cwd=cwd, env={**os.environ, **(env or {})})


def uv(*args: str, env: dict | None = None) -> int:
    return run(["uv", "run", *args], env=env)


def compose_files() -> list[str]:
    base = ROOT / "infra" / "compose" / "base.yml"
    others = sorted(p for p in (ROOT / "infra" / "compose").glob("*.yml") if p != base)
    return [arg for p in [base, *others] for arg in ("-f", str(p))]


def cmd_env(_: list[str]) -> int:
    target = ROOT / ".env"
    if target.exists():
        print(".env already exists; leaving it alone")
        return 0
    parts = []
    for example in sorted((ROOT / "infra" / "env").glob("*.env.example")):
        parts.append(f"# ---- from {example.relative_to(ROOT).as_posix()} ----\n{example.read_text(encoding='utf-8')}")
    target.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote .env from {len(parts)} example file(s)")
    return 0


LITE = {"APP_ENV": "lite", "DATABASE_URL": "sqlite+aiosqlite:///./.data/argus.db", "EVENT_BUS": "memory",
        "REDIS_URL": "", "DB_AUTO_CREATE": "true", "LOG_JSON": "false"}


def cmd_api(args: list[str]) -> int:
    (ROOT / ".data").mkdir(exist_ok=True)
    if uv("python", "-m", "backend.seed", env=LITE):
        return 1
    return uv("uvicorn", "backend.core.app:create_app", "--factory", "--reload", "--port", "8000", *args, env=LITE)


def cmd_web(args: list[str]) -> int:
    app = args[0] if args else "operator"
    front = ROOT / "frontend"
    if not (front / "node_modules").exists():
        run([*PNPM, "install"], cwd=front)
    return run([*PNPM, "--filter", f"@argus/{app}", "dev"], cwd=front)


def cmd_up(args: list[str]) -> int:
    return run(["docker", "compose", "--env-file", ".env", *compose_files(), "up", "--build", "-d", *args])


def cmd_down(args: list[str]) -> int:
    return run(["docker", "compose", *compose_files(), "down", *args])


def cmd_migrate(_: list[str]) -> int:
    return uv("alembic", "upgrade", "heads")


def cmd_revision(args: list[str]) -> int:
    import argparse

    p = argparse.ArgumentParser(prog="dev.py revision")
    p.add_argument("--module", required=True)
    p.add_argument("-m", "--message", required=True)
    p.add_argument("--no-autogenerate", action="store_true")
    a = p.parse_args(args)
    mig_root = ROOT / "backend" / "migrations"
    folder = mig_root / a.module
    first = not any(folder.glob("*.py"))
    cmd = ["alembic", "revision", "-m", a.message]
    if not a.no_autogenerate:
        cmd.append("--autogenerate")
    cmd += ["--head", "base", "--branch-label", a.module] if first else ["--head", f"{a.module}@head"]
    before = set(mig_root.glob("*.py"))
    if code := uv(*cmd):
        return code
    folder.mkdir(parents=True, exist_ok=True)
    for new in set(mig_root.glob("*.py")) - before:
        new.rename(folder / new.name)
        print(f"moved {new.name} -> {folder.relative_to(ROOT).as_posix()}/  (review it: autogenerate "
              "includes every model; keep only YOUR module's tables)")
    return 0


def cmd_seed(_: list[str]) -> int:
    return uv("python", "-m", "backend.seed")


def cmd_sim(args: list[str]) -> int:
    return uv("python", "-m", "simulator.core.cli", *args)


def cmd_test(args: list[str]) -> int:
    target = [f"backend/tests/{args[0]}", *args[1:]] if args and not args[0].startswith("-") else args
    return uv("pytest", *target)


def cmd_lint(_: list[str]) -> int:
    return uv("ruff", "check", "backend", "simulator", "scripts")


def cmd_contracts(_: list[str]) -> int:
    if code := uv("python", "scripts/contracts.py", "export"):
        return code
    if code := uv("python", "scripts/contracts.py", "check"):
        return code
    front = ROOT / "frontend"
    if (front / "node_modules").exists():
        return run([*PNPM, "--filter", "@argus/api-client", "generate"], cwd=front)
    print("frontend/node_modules missing: skipped API client generation (run `python scripts/dev.py web` once)")
    return 0


COMMANDS = {name[4:]: fn for name, fn in globals().items() if name.startswith("cmd_")}


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        return 1
    return COMMANDS[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    sys.exit(main())
