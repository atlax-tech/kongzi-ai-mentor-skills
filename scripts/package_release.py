#!/usr/bin/env python3
"""Build a public release tree without internal Harness/product documentation."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


ALLOWLIST = (
    ".github",
    "agents",
    "assets",
    "references",
    "scripts",
    "skills",
    "tests",
    ".gitignore",
    "LICENSE",
    "README.md",
    "SKILL.md",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=".")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    source = Path(args.source).resolve()
    output = Path(args.output).resolve()
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"输出目录必须为空：{output}")
    output.mkdir(parents=True, exist_ok=True)
    copied = []
    for name in ALLOWLIST:
        item = source / name
        if not item.exists():
            continue
        destination = output / name
        if item.is_dir():
            shutil.copytree(item, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else:
            shutil.copy2(item, destination)
        copied.append(name)
    forbidden = [str(path.relative_to(output)) for path in output.rglob("*") if path.name == "AGENTS.md"]
    if forbidden:
        raise SystemExit(f"发布包包含禁用文件：{forbidden}")
    print(json.dumps({"output": str(output), "copied": copied}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
