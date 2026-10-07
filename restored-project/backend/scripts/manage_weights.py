#!/usr/bin/env python
"""CLI for safe ALI model/adapter/GGUF artifact management."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from model.registry import ModelRegistry
from model.weights_manager import WeightsManager


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="ali-weights")
    sub = p.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("inspect"); q.add_argument("path")
    q = sub.add_parser("install"); q.add_argument("path"); q.add_argument("--type", choices=WeightsManager.TYPES); q.add_argument("--name", default="ALI"); q.add_argument("--version")
    q = sub.add_parser("verify"); q.add_argument("path")
    q = sub.add_parser("scan");
    q = sub.add_parser("list"); q.add_argument("--name", default="ALI")
    q = sub.add_parser("promote"); q.add_argument("name"); q.add_argument("version")
    args = p.parse_args(argv)
    registry = ModelRegistry(ROOT / "models" / "models.sqlite3")
    manager = WeightsManager(ROOT, registry)

    if args.cmd == "inspect":
        result = manager.inspect(args.path)
    elif args.cmd == "install":
        result = manager.install(args.path, artifact_type=args.type, name=args.name, version=args.version)
    elif args.cmd == "verify":
        result = manager.verify(args.path)
    elif args.cmd == "scan":
        result = manager.scan_inbox()
    elif args.cmd == "list":
        result = registry.list(args.name)
    else:
        registry.promote(args.name, args.version)
        result = {"promoted": True, "name": args.name, "version": args.version}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
