from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core.config import load_config
from .core.contracts import ExecutionRequest, Operation
from .core.orchestrator import Orchestrator
from .ops.doctor import inspect


def _runtime() -> tuple[Orchestrator, object]:
    config = load_config()
    repo_root = Path(__file__).resolve().parents[1]
    return Orchestrator(config, repo_root), config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ali-pro", description="ALI Studio Pro professional runtime")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("health")
    sub.add_parser("doctor")
    prep = sub.add_parser("prepare")
    prep.add_argument("text")
    run = sub.add_parser("execute")
    run.add_argument("text")
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--approve", action="store_true")
    run.add_argument("--write", action="append", default=[], metavar="PATH=CONTENT")
    run.add_argument("--check", action="append", default=[])
    sub.add_parser("serve")
    args = parser.parse_args(argv)

    if args.command == "doctor":
        print(json.dumps(inspect(), ensure_ascii=False, indent=2))
        return 0

    runtime, config = _runtime()
    try:
        if args.command == "health":
            print(json.dumps(runtime.health(), ensure_ascii=False, indent=2))
            return 0
        if args.command == "prepare":
            result = runtime.prepare(args.text)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result.get("project_id") else 2
        if args.command == "execute":
            operations = []
            for item in args.write:
                if "=" not in item:
                    parser.error("--write requires PATH=CONTENT")
                path, content = item.split("=", 1)
                operations.append(Operation("write", path, content))
            request = ExecutionRequest(text=args.text, operations=operations, checks=args.check, approved=args.approve, dry_run=args.dry_run)
            result = runtime.execute(request)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result.get("ok") or result.get("status") in {"approval_required", "dry_run"} else 3
        if args.command == "serve":
            from .api.server import ALIServer
            server = ALIServer(runtime, config)
            print(f"ALI API listening on http://{config.host}:{config.port}")
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
            finally:
                server.shutdown()
            return 0
        parser.error("unknown command")
    finally:
        if args.command != "serve":
            runtime.close()


if __name__ == "__main__":
    raise SystemExit(main())
