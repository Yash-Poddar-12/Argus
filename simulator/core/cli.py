"""Simulator CLI: ``python scripts/dev.py sim --scenario S1 --seed 42 [--demo-g1] [--speed 1]``.

``--demo-g1`` also drives the Gate G1 story through the API: the supervisor assigns
OP1001 -> EXC001 -> TASK001, and the operator confirms the machine, passes the pre-check and starts the task.
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime

import httpx

from simulator.core.engine import Simulation
from simulator.core.scenario import discover
from simulator.core.sinks import HttpSink, JsonlSink


def drive_g1(api: str, password: str, task_id: str = "TASK001", operator: str = "OP1001", machine: str = "EXC001") -> None:
    with httpx.Client(base_url=api.rstrip("/"), timeout=30) as c:
        def token(user: str) -> dict:
            r = c.post("/api/v1/auth/login", json={"username": user, "password": password})
            r.raise_for_status()
            return {"Authorization": f"Bearer {r.json()['access_token']}"}

        sup, op = token("sup001"), token(operator.lower())
        task = c.get(f"/api/v1/tasks/{task_id}", headers=sup).json()
        if task.get("status") == "PLANNED":
            c.post(f"/api/v1/tasks/{task_id}/assign", headers=sup,
                   json={"operator_id": operator, "machine_id": machine}).raise_for_status()
            print(f"[g1] supervisor assigned {operator} -> {machine} -> {task_id}")
        c.post(f"/api/v1/operators/{operator}/machine/confirm", headers=op, json={"machine_id": machine}).raise_for_status()
        items = c.get(f"/api/v1/machines/{machine}/precheck", headers=op).json()["items"]
        c.post(f"/api/v1/machines/{machine}/precheck", headers=op,
               json={"results": [{"item_id": i["item_id"], "ok": True} for i in items]}).raise_for_status()
        print(f"[g1] {operator} confirmed {machine} and passed the pre-operation check")
        r = c.post(f"/api/v1/tasks/{task_id}/start", headers=op)
        if r.status_code == 200:
            print(f"[g1] {operator} started {task_id}")
        else:
            print(f"[g1] start skipped: {r.json().get('error', {}).get('message')}")


def main(argv: list[str] | None = None) -> int:
    scenarios = discover()
    ap = argparse.ArgumentParser(description="Argus deterministic simulator")
    ap.add_argument("--scenario", default="S1", choices=sorted(scenarios))
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--duration", type=float, default=3600, help="simulated seconds")
    ap.add_argument("--speed", type=float, default=1,
                    help="x real time (1 = live). >1 compresses time: readings get future timestamps, so the twin's "
                         "freshness goes negative. 0 = as fast as possible (backfill/datasets)")
    ap.add_argument("--emit-every", type=float, default=5, help="telemetry interval in simulated seconds")
    ap.add_argument("--machines", default="EXC001,DMP001,DMP002")
    ap.add_argument("--start", help="ISO start time (default: now, UTC). Fix it for reproducible datasets")
    ap.add_argument("--sink", choices=["http", "stdout"], default="http")
    ap.add_argument("--api", default="http://localhost:8000")
    ap.add_argument("--user", default="sup001")
    ap.add_argument("--password", default="demo1234")
    ap.add_argument("--demo-g1", action="store_true", help="assign + confirm + pre-check + start TASK001 first")
    ap.add_argument("--list", action="store_true", help="list scenarios and exit")
    args = ap.parse_args(argv)

    if args.list:
        for sid, cls in sorted(scenarios.items()):
            print(f"{sid:4} {cls.title:28} owner={cls.owner}  {cls.description}")
        return 0
    start = datetime.fromisoformat(args.start.replace("Z", "+00:00")) if args.start else None
    sim = Simulation(seed=args.seed, start=start, machines=args.machines.split(","), scenario=scenarios[args.scenario](),
                     emit_every_s=args.emit_every)
    if args.sink == "http" and args.demo_g1:
        drive_g1(args.api, args.password)
    sink = HttpSink(args.api, args.user, args.password) if args.sink == "http" else JsonlSink()
    if args.sink == "http":
        print(f"[sim] {args.scenario} seed={args.seed} machines={args.machines} -> {args.api} at {args.speed}x "
              f"(Ctrl+C to stop)", file=sys.stderr)
    last_t = 0.0
    try:
        for kind, item in sim.run(args.duration):
            if kind == "conditions":
                sink.conditions(item)
                continue
            t = (datetime.fromisoformat(item["ts"].replace("Z", "+00:00")) - sim.start).total_seconds()
            if args.speed and args.sink == "http" and t > last_t:
                sink.flush()
                time.sleep((t - last_t) / args.speed)
                last_t = t
            sink.telemetry(item)
    except KeyboardInterrupt:
        pass
    finally:
        sink.close()
    if args.sink == "http":
        print(f"[sim] sent {sink.sent} telemetry points", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
