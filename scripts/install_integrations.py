#!/usr/bin/env python3
"""Install Kongzi's four upstream skill integrations into an Agent Skills directory."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


INTEGRATIONS = {
    "cangjie": {
        "repo": "https://github.com/kangarooking/cangjie-skill.git",
        "destination": "cangjie-skill",
        "subdir": None,
    },
    "nuwa": {
        "repo": "https://github.com/alchaincyf/nuwa-skill.git",
        "destination": "nuwa-skill",
        "subdir": None,
    },
    "darwin": {
        "repo": "https://github.com/alchaincyf/darwin-skill.git",
        "destination": "darwin-skill",
        "subdir": None,
    },
    "video-downloader": {
        "repo": "https://github.com/kangarooking/kangarooking-skills.git",
        "destination": "video-downloader",
        "subdir": "video-downloader",
    },
}


class InstallError(RuntimeError):
    pass


def run(command: list[str], cwd: Path | None = None, retries: int = 2) -> None:
    completed = None
    for attempt in range(retries + 1):
        completed = subprocess.run(command, cwd=cwd, check=False, capture_output=True, text=True)
        if completed.returncode == 0:
            return
        if attempt < retries:
            time.sleep(1 + attempt)
    assert completed is not None
    raise InstallError(
        f"命令失败：{' '.join(command)}\n{completed.stderr.strip() or completed.stdout.strip()}"
    )


def install_one(name: str, target: Path, force: bool) -> dict[str, str]:
    spec = INTEGRATIONS[name]
    destination = target / spec["destination"]
    if destination.exists() and not force:
        if (destination / "SKILL.md").exists():
            return {"name": name, "status": "already-installed", "path": str(destination)}
        raise InstallError(f"目标已存在但不是有效 skill：{destination}；检查后显式使用 --force")

    target.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"kongzi-{name}-") as raw_temp:
        temp = Path(raw_temp)
        clone = temp / "repo"
        if spec["subdir"]:
            # A normal shallow clone is more reliable than a promisor/sparse clone on
            # intermittent networks; only the requested skill directory is copied.
            run(["git", "clone", "--depth", "1", spec["repo"], str(clone)])
            source = clone / spec["subdir"]
        else:
            run(["git", "clone", "--depth", "1", spec["repo"], str(clone)])
            source = clone
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=clone,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        if not (source / "SKILL.md").exists():
            raise InstallError(f"上游 {name} 未包含预期的 SKILL.md：{source}")
        staged = target / f".{spec['destination']}.installing-{os.getpid()}"
        if staged.exists():
            shutil.rmtree(staged)
        shutil.copytree(source, staged, ignore=shutil.ignore_patterns(".git"))
        (staged / "UPSTREAM.json").write_text(
            json.dumps(
                {
                    "name": name,
                    "repository": spec["repo"],
                    "subdir": spec["subdir"],
                    "revision": revision,
                    "installed_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        if destination.exists():
            backup = target / f".{spec['destination']}.backup"
            if backup.exists():
                raise InstallError(f"备份路径已存在，拒绝覆盖：{backup}")
            destination.replace(backup)
        staged.replace(destination)
    return {
        "name": name,
        "status": "installed",
        "path": str(destination),
        "revision": revision,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="安装 Kongzi 的完整上游 skill 集成")
    parser.add_argument(
        "--target",
        default=str(Path.home() / ".claude" / "skills"),
        help="Agent Skills 目录；Claude Code 默认 ~/.claude/skills",
    )
    parser.add_argument(
        "--only",
        action="append",
        choices=tuple(INTEGRATIONS),
        help="只安装指定集成；可重复传入",
    )
    parser.add_argument("--force", action="store_true", help="备份并替换已有非空集成")
    parser.add_argument("--dry-run", action="store_true", help="仅显示计划，不写入")
    args = parser.parse_args()
    target = Path(args.target).expanduser().resolve()
    selected = args.only or list(INTEGRATIONS)
    plan = [
        {
            "name": name,
            "repo": INTEGRATIONS[name]["repo"],
            "subdir": INTEGRATIONS[name]["subdir"],
            "destination": str(target / INTEGRATIONS[name]["destination"]),
        }
        for name in selected
    ]
    if args.dry_run:
        print(json.dumps({"target": str(target), "plan": plan}, ensure_ascii=False, indent=2))
        return 0
    if not shutil.which("git"):
        print(json.dumps({"ok": False, "error": "未找到 git"}, ensure_ascii=False), file=sys.stderr)
        return 2
    try:
        results = [install_one(name, target, args.force) for name in selected]
    except InstallError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps({"target": str(target), "results": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
