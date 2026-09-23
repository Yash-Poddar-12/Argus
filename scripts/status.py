#!/usr/bin/env python3
"""Module status helper for parallel, multi-IDE teamwork.

Stdlib only; works on Windows, macOS and Linux.

  python scripts/status.py board [--markdown]
      Live board computed from every docs/03-modules/M*/STATUS.md.

  python scripts/status.py log --action PUSH --msg "..." [--module M02]
                               [--wp M02-WP1=DONE ...] [--state IN_PROGRESS] [--handle you]
      With --module: updates that module's STATUS.md (Last updated, optional WP/module
      state, new line under "Update log"). Always appends to your own sync log
      docs/05-status/sync-log/<handle>.md.

  python scripts/status.py changes [--since REF]
      After a pull: which contracts, catalogs and module statuses changed since REF
      (default ORIG_HEAD, which git sets on pull/merge/rebase).

See docs/04-workflow/SYNC_PROTOCOL.md.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULES_DIR = ROOT / "docs" / "03-modules"
SYNC_DIR = ROOT / "docs" / "05-status" / "sync-log"
LOG_MARKER = "<!-- log:insert -->"
STATES = {"NOT_STARTED", "IN_PROGRESS", "MOCKED", "BLOCKED", "IN_REVIEW", "DONE"}
ACTIONS = {"PUSH", "PULL", "MERGE", "REBASE", "INIT", "NOTE"}
WATCHED = ["contracts", "docs/02-contracts", "docs/03-modules", "MASTER_PROJECT_CONTEXT_AND_EXECUTION_PLAN.md", "AGENTS.md"]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ---------- helpers ----------

def git(*args: str) -> str:
    try:
        out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    except FileNotFoundError:
        return ""
    return out.stdout.strip() if out.returncode == 0 else ""


def default_handle() -> str:
    return (os.environ.get("STATUS_HANDLE") or git("config", "github.user")
            or git("config", "user.name") or "unknown").replace(" ", "-").lstrip("@")


def read(path: Path) -> tuple[str, str]:
    raw = path.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    return raw.replace("\r\n", "\n"), nl


def write(path: Path, text: str, nl: str) -> None:
    path.write_bytes(text.replace("\n", nl).encode("utf-8"))


def find_status(module: str) -> Path:
    mod = module.upper()
    if not re.fullmatch(r"M\d{2}", mod):
        sys.exit(f"--module must look like M02, got {module!r}")
    hits = sorted(MODULES_DIR.glob(f"{mod}-*/STATUS.md"))
    if not hits:
        sys.exit(f"No STATUS.md found for {mod} under {MODULES_DIR}")
    return hits[0]


def table_rows(lines: list[str]) -> list[list[str]]:
    rows = []
    for ln in lines:
        s = ln.strip()
        if s.startswith("|") and not re.fullmatch(r"\|[\s:|-]+\|", s):
            rows.append([c.strip() for c in s.strip("|").split("|")])
    return rows


def parse_status(path: Path) -> dict:
    text, _ = read(path)
    summary: dict[str, str] = {}
    m = re.search(r"<!-- status:summary.*?-->(.*?)<!-- /status:summary -->", text, re.S)
    if m:
        for row in table_rows(m.group(1).splitlines())[1:]:
            if len(row) >= 2:
                summary[row[0]] = row[1]
    wps = []
    wp_section = re.search(r"## Work packages\n(.*?)(\n## |\Z)", text, re.S)
    if wp_section:
        for row in table_rows(wp_section.group(1).splitlines()):
            if row and re.match(r"M\d{2}-", row[0]) and len(row) >= 3:
                wps.append({"id": row[0], "title": row[1], "state": row[2]})
    blockers = []
    b = re.search(r"## Blockers\n(.*?)(\n## |\Z)", text, re.S)
    if b:
        blockers = [ln[2:].strip() for ln in b.group(1).splitlines()
                    if ln.startswith("- ") and ln[2:].strip().lower() != "none"]
    return {"path": path, "summary": summary, "wps": wps, "blockers": blockers}


def set_table_value(text: str, key: str, value: str) -> str:
    pat = re.compile(rf"^(\|\s*{re.escape(key)}\s*\|)[^|\n]*(\|)", re.M)
    if not pat.search(text):
        sys.exit(f"Could not find '{key}' row in STATUS summary table")
    return pat.sub(lambda m: f"{m.group(1)} {value} {m.group(2)}", text, count=1)


def set_wp_state(text: str, wp: str, state: str) -> str:
    pat = re.compile(rf"^(\|\s*{re.escape(wp)}\s*\|[^|\n]*\|)[^|\n]*(\|)", re.M)
    if not pat.search(text):
        sys.exit(f"Work package {wp} not found in STATUS.md")
    return pat.sub(lambda m: f"{m.group(1)} {state} {m.group(2)}", text, count=1)


def insert_log(text: str, line: str, path: Path) -> str:
    if LOG_MARKER not in text:
        sys.exit(f"{path} is missing the '{LOG_MARKER}' marker under 'Update log'")
    return text.replace(LOG_MARKER, f"{LOG_MARKER}\n{line}", 1)


# ---------- commands ----------

def cmd_board(args: argparse.Namespace) -> None:
    paths = sorted(MODULES_DIR.glob("M[0-9][0-9]-*/STATUS.md"))
    if not paths:
        sys.exit("No module STATUS.md files found.")
    header = ["Module", "Owner", "Phase", "State", "WPs done", "Active WPs", "Blockers", "Last updated"]
    rows = []
    for p in paths:
        s = parse_status(p)
        sm, wps = s["summary"], s["wps"]
        done = sum(1 for w in wps if w["state"] == "DONE")
        active = ", ".join(w["id"].split("-", 1)[1] for w in wps if w["state"] in {"IN_PROGRESS", "IN_REVIEW", "BLOCKED"})
        rows.append([
            f'{sm.get("Module", p.parent.name[:3])} {p.parent.name[4:]}', sm.get("Owner", "?"), sm.get("Phase", "?"),
            sm.get("State", "?"), f"{done}/{len(wps)}", active or "-", str(len(s["blockers"])) if s["blockers"] else "-",
            sm.get("Last updated", "?"),
        ])
    if args.markdown:
        print("| " + " | ".join(header) + " |")
        print("|" + "|".join("---" for _ in header) + "|")
        for r in rows:
            print("| " + " | ".join(r) + " |")
    else:
        widths = [max(len(header[i]), *(len(r[i]) for r in rows)) for i in range(len(header))]
        fmt = "  ".join(f"{{:<{w}}}" for w in widths)
        print(fmt.format(*header))
        print(fmt.format(*("-" * w for w in widths)))
        for r in rows:
            print(fmt.format(*r))
    blocked = [(p, parse_status(p)["blockers"]) for p in paths]
    blocked = [(p, b) for p, b in blocked if b]
    if blocked:
        print("\nBlockers:")
        for p, bl in blocked:
            for item in bl:
                print(f"  {p.parent.name}: {item}")


def cmd_log(args: argparse.Namespace) -> None:
    action = args.action.upper()
    if action not in ACTIONS:
        sys.exit(f"--action must be one of {sorted(ACTIONS)}")
    handle = (args.handle or default_handle()).lstrip("@")
    today = dt.date.today().isoformat()
    branch = git("rev-parse", "--abbrev-ref", "HEAD") or "-"
    sha = git("rev-parse", "--short", "HEAD") or "-"
    ref = f"{branch}@{sha}" if action in {"PULL", "MERGE", "REBASE"} else branch
    msg = " ".join(args.msg.split())

    if args.module:
        path = find_status(args.module)
        text, nl = read(path)
        for spec in args.wp or []:
            if "=" not in spec:
                sys.exit(f"--wp expects WP=STATE, got {spec!r}")
            wp, state = spec.split("=", 1)
            state = state.upper()
            if state not in STATES:
                sys.exit(f"Unknown state {state!r}; allowed: {sorted(STATES)}")
            text = set_wp_state(text, wp.strip().upper(), state)
        if args.state:
            state = args.state.upper()
            if state not in STATES:
                sys.exit(f"Unknown state {state!r}; allowed: {sorted(STATES)}")
            text = set_table_value(text, "State", state)
        if args.focus:
            text = set_table_value(text, "Current focus", args.focus)
        text = set_table_value(text, "Last updated", f"{today} · @{handle} · {msg[:60]}")
        text = insert_log(text, f"- {today} · @{handle} · {action} · {ref} · {msg}", path)
        write(path, text, nl)
        print(f"Updated {path.relative_to(ROOT)}")

    SYNC_DIR.mkdir(parents=True, exist_ok=True)
    person = SYNC_DIR / f"{handle}.md"
    if not person.exists():
        template = SYNC_DIR / "_TEMPLATE.md"
        base = template.read_text(encoding="utf-8") if template.exists() else f"# Sync log · @handle\n\n{LOG_MARKER}\n"
        write(person, base.replace("\r\n", "\n").replace("@handle", f"@{handle}"), "\n")
    text, nl = read(person)
    mod = f"{args.module.upper()} · " if args.module else ""
    text = insert_log(text, f"- {today} · {action} · {mod}{ref} · {msg}", person)
    write(person, text, nl)
    print(f"Updated {person.relative_to(ROOT)}")
    if args.module and action == "PUSH":
        print("Remember: commit the STATUS.md change together with your code before pushing.")


def cmd_changes(args: argparse.Namespace) -> None:
    since = args.since
    if not git("rev-parse", "--verify", "--quiet", since):
        sys.exit(f"Ref {since!r} not found. After 'git pull' ORIG_HEAD exists; otherwise pass --since <sha|branch>.")
    head = git("rev-parse", "--short", "HEAD")
    print(f"Changes in shared areas: {since} -> HEAD ({head})\n")
    stat = git("diff", "--stat", since, "HEAD", "--", *WATCHED)
    print(stat or "  (no changes to contracts, catalogs, module docs, master plan or AGENTS.md)")

    contract_files = git("diff", "--name-only", since, "HEAD", "--", "contracts", "docs/02-contracts").splitlines()
    if contract_files:
        print("\n!! Contract / catalog changes: check whether you consume these:")
        for f in contract_files:
            print(f"   - {f}")

    diff = git("diff", "-U0", since, "HEAD", "--", "docs/03-modules/*/STATUS.md")
    current = None
    lines = []
    for ln in diff.splitlines():
        if ln.startswith("+++ b/"):
            current = ln[6:].split("/")[2] if ln.count("/") >= 3 else ln[6:]
        elif ln.startswith("+- ") and current:
            lines.append(f"   [{current}] {ln[3:]}")
    if lines:
        print("\nNew module status log lines:")
        print("\n".join(lines))
    print("\nNext: note anything that affects you with\n"
          "  python scripts/status.py log --action PULL --msg \"pulled develop; <what you noticed>\"")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("board", help="print the live module status board")
    b.add_argument("--markdown", action="store_true", help="print as a markdown table")
    b.set_defaults(func=cmd_board)

    lg = sub.add_parser("log", help="record a push/pull (module STATUS.md and/or your sync log)")
    lg.add_argument("--action", required=True, help="PUSH | PULL | MERGE | REBASE | NOTE")
    lg.add_argument("--msg", required=True, help="one-line summary")
    lg.add_argument("--module", help="module id, e.g. M02 (required for PUSH of module work)")
    lg.add_argument("--wp", action="append", help="set a WP state, e.g. M02-WP1=DONE (repeatable)")
    lg.add_argument("--state", help="set the module State")
    lg.add_argument("--focus", help="set 'Current focus'")
    lg.add_argument("--handle", help="your GitHub handle (default: $STATUS_HANDLE, git github.user, git user.name)")
    lg.set_defaults(func=cmd_log)

    ch = sub.add_parser("changes", help="show shared-area changes since a ref (default ORIG_HEAD)")
    ch.add_argument("--since", default="ORIG_HEAD")
    ch.set_defaults(func=cmd_changes)

    args = ap.parse_args()
    if args.cmd == "log" and args.action.upper() == "PUSH" and not args.module:
        print("Note: PUSH without --module only updates your sync log, not a module STATUS.md.")
    args.func(args)


if __name__ == "__main__":
    main()
