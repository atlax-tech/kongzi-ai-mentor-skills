#!/usr/bin/env python3
"""Kongzi: a source-grounded, local-first learning coach state engine.

The agent owns teaching judgment and dialogue. This CLI owns durable state,
evidence provenance, review scheduling, reports, and integration hand-offs.
It intentionally depends only on Python's standard library.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import io
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


SCHEMA_VERSION = 1
REVIEW_INTERVALS = (1, 3, 7, 14, 30, 60, 120)
KNOWLEDGE_TYPES = {"concept", "procedure", "fact", "mental-model", "metacognitive"}
AUTHORITY_LEVELS = {"primary", "official", "standard", "textbook", "secondary", "user"}
QUESTION_KINDS = {"recall", "explain", "compare", "application", "debug", "create"}
DEFAULT_MASTERY_CRITERIA = {
    "fact": {"threshold": 0.85, "delayed_passes": 2, "requires_application": True},
    "concept": {"threshold": 0.80, "delayed_passes": 2, "requires_application": True},
    "procedure": {"threshold": 0.85, "delayed_passes": 2, "requires_application": True},
    "mental-model": {"threshold": 0.80, "delayed_passes": 2, "requires_application": True},
    "metacognitive": {"threshold": 0.80, "delayed_passes": 2, "requires_application": True},
}
UTC = dt.timezone.utc


class KongziError(RuntimeError):
    pass


def now() -> dt.datetime:
    return dt.datetime.now(UTC)


def iso(value: dt.datetime | None = None) -> str:
    return (value or now()).replace(microsecond=0).isoformat()


def parse_datetime(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def vault_timezone(vault: "Vault") -> ZoneInfo:
    name = json_load(vault.config_path, {}).get("timezone", "UTC")
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError as exc:
        raise KongziError(f"未知时区：{name}") from exc


def local_now(vault: "Vault") -> dt.datetime:
    return now().astimezone(vault_timezone(vault))


def slugify(value: str, fallback: str = "item") -> str:
    value = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", value.strip().lower(), flags=re.UNICODE)
    value = re.sub(r"-+", "-", value).strip("-_")
    return value[:60] or fallback


def new_id(prefix: str) -> str:
    return f"{prefix}_{now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_load(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise KongziError(f"状态文件损坏：{path}: {exc}") from exc


def json_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if path.exists():
        shutil.copy2(path, path.with_suffix(path.suffix + ".bak"))
    temp.replace(path)


def append_jsonl(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")


def emit(value: Any, human: str | None = None) -> None:
    if human:
        print(human)
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def parse_scalar(value: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def md_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


class TextExtractor(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "canvas"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.title = ""
        self._skip_depth = 0
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in self.SKIP:
            self._skip_depth += 1
        if tag == "title":
            self._in_title = True
        if tag in {"p", "div", "article", "section", "h1", "h2", "h3", "li", "br"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self.SKIP and self._skip_depth:
            self._skip_depth -= 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        cleaned = re.sub(r"\s+", " ", html.unescape(data)).strip()
        if not cleaned:
            return
        if self._in_title:
            self.title = f"{self.title} {cleaned}".strip()
        self.parts.append(cleaned)

    def text(self) -> str:
        joined = " ".join(self.parts)
        joined = re.sub(r" *\n *", "\n", joined)
        joined = re.sub(r"\n{3,}", "\n\n", joined)
        return joined.strip()


class Vault:
    def __init__(self, root: Path):
        self.root = root.expanduser().resolve()
        self.meta = self.root / ".kongzi"
        self.notes = self.root / "Kongzi"
        self.config_path = self.meta / "config.json"
        self.profile_path = self.meta / "profile.json"
        self.state_path = self.meta / "state.json"
        self.events_path = self.meta / "events.jsonl"
        self.queue_path = self.meta / "review-queue.json"
        self.integrations_path = self.meta / "integrations.json"

    def require(self) -> None:
        if not self.config_path.exists():
            raise KongziError(
                f"未找到 Kongzi 状态：{self.root}。先运行：python3 scripts/kongzi.py init --vault {self.root}"
            )

    def config(self) -> dict[str, Any]:
        self.require()
        return json_load(self.config_path, {})

    def state(self) -> dict[str, Any]:
        self.require()
        return json_load(self.state_path, {})

    def profile(self) -> dict[str, Any]:
        self.require()
        return json_load(self.profile_path, {})

    def queue(self) -> dict[str, Any]:
        self.require()
        return json_load(self.queue_path, {"schema_version": SCHEMA_VERSION, "cards": {}})

    def save_state(self, state: dict[str, Any]) -> None:
        state["updated_at"] = iso()
        json_write(self.state_path, state)

    def save_profile(self, profile: dict[str, Any]) -> None:
        profile["updated_at"] = iso()
        json_write(self.profile_path, profile)

    def save_queue(self, queue: dict[str, Any]) -> None:
        queue["updated_at"] = iso()
        json_write(self.queue_path, queue)

    def event(
        self,
        event_type: str,
        payload: dict[str, Any],
        journey_id: str | None = None,
    ) -> dict[str, Any]:
        event = {
            "id": new_id("evt"),
            "schema_version": SCHEMA_VERSION,
            "at": iso(),
            "type": event_type,
            "journey_id": journey_id or active_journey_id(self),
            "payload": payload,
        }
        append_jsonl(self.events_path, event)
        return event

    def events(self) -> list[dict[str, Any]]:
        if not self.events_path.exists():
            return []
        result = []
        for line_number, line in enumerate(
            self.events_path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not line.strip():
                continue
            try:
                result.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise KongziError(f"事件日志第 {line_number} 行损坏") from exc
        return result


def active_journey_id(vault: Vault) -> str | None:
    config = json_load(vault.config_path, {})
    return config.get("active_journey_id")


def require_journey(vault: Vault) -> tuple[str, dict[str, Any], dict[str, Any]]:
    state = vault.state()
    journey_id = active_journey_id(vault)
    if not journey_id or journey_id not in state.get("journeys", {}):
        raise KongziError("尚未选择学习旅程；运行 journey create 或 journey select")
    return journey_id, state["journeys"][journey_id], state


def initialize(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    if args.daily_minutes <= 0 or not 1 <= args.days_per_week <= 7:
        raise KongziError("daily-minutes 必须大于 0，days-per-week 必须在 1 到 7 之间")
    vault.root.mkdir(parents=True, exist_ok=True)
    if vault.config_path.exists() and not args.force:
        raise KongziError(f"{vault.root} 已初始化；如需重建，显式传入 --force")
    for directory in (
        vault.meta,
        vault.notes,
        vault.notes / "Sources",
        vault.notes / "Journeys",
        vault.notes / "Reports" / "Daily",
        vault.notes / "Reports" / "Weekly",
        vault.notes / "Mentors",
        vault.notes / "Inbox",
    ):
        directory.mkdir(parents=True, exist_ok=True)
    config = {
        "schema_version": SCHEMA_VERSION,
        "initialized_at": iso(),
        "updated_at": iso(),
        "vault_root": str(vault.root),
        "locale": args.locale,
        "timezone": args.timezone,
        "active_journey_id": None,
        "knowledge_base": {
            "type": "obsidian",
            "mode": args.knowledge_base,
            "path": str(vault.root),
        },
        "reminders": {"method": None, "time": "20:00", "installed": False},
    }
    profile = {
        "schema_version": SCHEMA_VERSION,
        "learner_name": args.name,
        "self_reported": {},
        "observed": {
            "strengths": [],
            "frictions": [],
            "preferred_formats": {},
            "calibration": [],
        },
        "interviews": [],
        "updated_at": iso(),
    }
    state = {
        "schema_version": SCHEMA_VERSION,
        "created_at": iso(),
        "updated_at": iso(),
        "journeys": {},
        "sources": {},
        "claims": {},
        "nodes": {},
        "plans": {},
        "sessions": {},
        "answers": {},
        "grades": {},
        "notes": {},
        "mentor": {"enabled": False, "name": None, "persona_path": None},
    }
    json_write(vault.config_path, config)
    json_write(vault.profile_path, profile)
    json_write(vault.state_path, state)
    json_write(vault.queue_path, {"schema_version": SCHEMA_VERSION, "cards": {}, "updated_at": iso()})
    json_write(vault.integrations_path, {"schema_version": SCHEMA_VERSION, "runs": {}})
    vault.events_path.write_text("", encoding="utf-8")
    dashboard = textwrap.dedent(
        f"""\
        # Kongzi 学习控制台

        > 学习者：{args.name or "未填写"}  
        > 初始化：{iso()}

        ## 下一步

        1. 完成画像访谈：`/Kongzi profile`
        2. 创建学习旅程：`/Kongzi journey`
        3. 录入来源材料：`/Kongzi source`

        ## 学习原则

        - 先证据，后讲解；事实主张必须回到来源与定位符。
        - 先尝试输出，再看答案；即时练习与延迟复习分开记录。
        - 自述偏好只作假设，真实表现用于逐步校准。
        """
    )
    (vault.notes / "Dashboard.md").write_text(dashboard, encoding="utf-8")
    event = vault.event("vault.initialized", {"learner_name": args.name})
    result: dict[str, Any] = {
        "vault": str(vault.root),
        "dashboard": str(vault.notes / "Dashboard.md"),
        "event_id": event["id"],
        "next": "profile questionnaire",
    }
    if args.goal:
        journey_args = argparse.Namespace(
            vault=str(vault.root),
            goal=args.goal,
            outcome=args.outcome or args.goal,
            prior_knowledge=args.prior_knowledge or "",
            deadline=args.deadline,
            daily_minutes=args.daily_minutes,
            days_per_week=args.days_per_week,
            constraints=args.constraints or "",
        )
        result["journey"] = create_journey(journey_args, emit_result=False)
    emit(result)


def questionnaire(args: argparse.Namespace) -> None:
    questions = [
        {
            "id": "goal",
            "question": "你希望能实际完成什么，而不仅是‘了解’什么？",
            "required": True,
        },
        {
            "id": "baseline",
            "question": "不查资料，用自己的话解释你已经知道的内容，并给一个例子。",
            "required": True,
        },
        {
            "id": "constraints",
            "question": "每周可用几天、每天多少分钟？有哪些不可改变的限制？",
            "required": True,
        },
        {
            "id": "deadline",
            "question": "是否有截止日期或需要交付的作品/考试？",
            "required": False,
        },
        {
            "id": "materials",
            "question": "你手头有哪些书、课程、论文、视频或工作材料？",
            "required": True,
        },
        {
            "id": "experience",
            "question": "过去学类似内容时，什么让你坚持，什么让你中断？",
            "required": True,
        },
        {
            "id": "accessibility",
            "question": "语言、设备、阅读、听力或注意力方面有无需要适配？",
            "required": False,
        },
        {
            "id": "diagnostic",
            "question": "完成一个最小诊断任务：写出该领域一个核心概念、一个操作步骤和一个常见错误。",
            "required": True,
        },
    ]
    emit({"questions": questions, "instruction": "逐题提问；不得一次替用户作答。"})


def set_profile(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    profile = vault.profile()
    target = profile.setdefault("self_reported", {})
    segments = args.field.split(".")
    for segment in segments[:-1]:
        target = target.setdefault(segment, {})
    target[segments[-1]] = parse_scalar(args.value)
    evidence = {
        "id": new_id("int"),
        "at": iso(),
        "field": args.field,
        "value": parse_scalar(args.value),
        "source": "learner-self-report",
    }
    profile.setdefault("interviews", []).append(evidence)
    vault.save_profile(profile)
    event = vault.event("profile.self_reported", evidence)
    emit({"updated": args.field, "event_id": event["id"]})


def observe_profile(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    if not 0 <= args.confidence <= 1:
        raise KongziError("confidence 必须在 0 到 1 之间")
    profile = vault.profile()
    observation = {
        "id": new_id("obs"),
        "at": iso(),
        "dimension": args.dimension,
        "observation": args.observation,
        "evidence_id": args.evidence_id,
        "confidence": args.confidence,
    }
    profile.setdefault("observed", {}).setdefault("calibration", []).append(observation)
    vault.save_profile(profile)
    event = vault.event("profile.observed", observation)
    emit({"observation": observation, "event_id": event["id"]})


def create_journey(args: argparse.Namespace, emit_result: bool = True) -> dict[str, Any]:
    vault = Vault(Path(args.vault))
    if args.daily_minutes <= 0 or not 1 <= args.days_per_week <= 7:
        raise KongziError("daily-minutes 必须大于 0，days-per-week 必须在 1 到 7 之间")
    state = vault.state()
    journey_id = new_id("journey")
    journey = {
        "id": journey_id,
        "slug": slugify(args.goal, "journey"),
        "goal": args.goal,
        "target_outcome": args.outcome,
        "prior_knowledge": args.prior_knowledge,
        "deadline": args.deadline,
        "constraints": args.constraints,
        "availability": {
            "daily_minutes": args.daily_minutes,
            "days_per_week": args.days_per_week,
        },
        "status": "intake",
        "created_at": iso(),
        "updated_at": iso(),
    }
    state.setdefault("journeys", {})[journey_id] = journey
    vault.save_state(state)
    config = vault.config()
    config["active_journey_id"] = journey_id
    config["updated_at"] = iso()
    json_write(vault.config_path, config)
    journey_dir = vault.notes / "Journeys" / journey["slug"]
    journey_dir.mkdir(parents=True, exist_ok=True)
    (journey_dir / "Journey.md").write_text(
        textwrap.dedent(
            f"""\
            # {args.goal}

            - 目标产出：{args.outcome}
            - 当前基础：{args.prior_knowledge or "待诊断"}
            - 截止日期：{args.deadline or "无硬截止"}
            - 可用时间：每周 {args.days_per_week} 天，每天 {args.daily_minutes} 分钟
            - 限制：{args.constraints or "无"}

            ## 完成定义

            只有在延迟提取与应用任务都通过后，知识点才标记为掌握。
            """
        ),
        encoding="utf-8",
    )
    event = vault.event("journey.created", journey, journey_id)
    result = {"journey": journey, "event_id": event["id"], "path": str(journey_dir)}
    if emit_result:
        emit(result)
    return result


def list_journeys(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    state = vault.state()
    emit(
        {
            "active_journey_id": active_journey_id(vault),
            "journeys": list(state.get("journeys", {}).values()),
        }
    )


def select_journey(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    state = vault.state()
    if args.journey_id not in state.get("journeys", {}):
        raise KongziError(f"未知旅程：{args.journey_id}")
    config = vault.config()
    config["active_journey_id"] = args.journey_id
    config["updated_at"] = iso()
    json_write(vault.config_path, config)
    event = vault.event("journey.selected", {"journey_id": args.journey_id}, args.journey_id)
    emit({"active_journey_id": args.journey_id, "event_id": event["id"]})


def extract_local(path: Path) -> tuple[str, bytes, str]:
    if not path.exists() or not path.is_file():
        raise KongziError(f"来源文件不存在：{path}")
    raw = path.read_bytes()
    suffix = path.suffix.lower()
    if suffix in {".md", ".txt", ".rst", ".csv", ".json", ".yaml", ".yml"}:
        return raw.decode("utf-8", errors="replace"), raw, suffix.lstrip(".") or "text"
    if suffix in {".html", ".htm"}:
        parser = TextExtractor()
        parser.feed(raw.decode("utf-8", errors="replace"))
        return parser.text(), raw, "html"
    if suffix == ".epub":
        parts = []
        with zipfile.ZipFile(path) as archive:
            for name in sorted(archive.namelist()):
                if name.lower().endswith((".html", ".xhtml", ".htm")):
                    parser = TextExtractor()
                    parser.feed(archive.read(name).decode("utf-8", errors="replace"))
                    parts.append(f"\n\n## {name}\n\n{parser.text()}")
        if not parts:
            raise KongziError("EPUB 中未找到可抽取文本")
        return "".join(parts).strip(), raw, "epub"
    if suffix == ".docx":
        with zipfile.ZipFile(path) as archive:
            try:
                document = archive.read("word/document.xml")
            except KeyError as exc:
                raise KongziError("DOCX 缺少 word/document.xml") from exc
        root = ET.fromstring(document)
        paragraphs = []
        for paragraph in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
            text = "".join(
                node.text or ""
                for node in paragraph.iter(
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"
                )
            ).strip()
            if text:
                paragraphs.append(text)
        return "\n\n".join(paragraphs), raw, "docx"
    if suffix == ".pdf":
        return extract_pdf(raw, path), raw, "pdf"
    raise KongziError(f"暂不支持的本地来源格式：{suffix}")


def extract_pdf(raw: bytes, path: Path | None = None) -> str:
    try:
        import pypdf  # type: ignore

        reader = pypdf.PdfReader(io.BytesIO(raw))
        pages = []
        for index, page in enumerate(reader.pages, start=1):
            pages.append(f"\n\n## Page {index}\n\n{page.extract_text() or ''}")
        return "".join(pages).strip()
    except ImportError:
        pass
    except Exception as exc:
        raise KongziError(f"pypdf 解析失败：{exc}") from exc
    tool = shutil.which("pdftotext")
    if not tool:
        raise KongziError("读取 PDF 需要 pypdf 或系统命令 pdftotext")
    if path is not None:
        completed = subprocess.run(
            [tool, "-layout", str(path), "-"],
            check=False,
            capture_output=True,
            text=True,
        )
    else:
        completed = subprocess.run(
            [tool, "-layout", "-", "-"],
            input=raw,
            check=False,
            capture_output=True,
        )
        completed.stdout = completed.stdout.decode("utf-8", errors="replace")
        completed.stderr = completed.stderr.decode("utf-8", errors="replace")
    if completed.returncode:
        raise KongziError(f"pdftotext 失败：{completed.stderr.strip()}")
    return completed.stdout


def persist_source(
    vault: Vault,
    title: str,
    text: str,
    raw_hash: str,
    origin: str,
    source_kind: str,
    authority: str,
    published_at: str | None,
    author: str | None,
    retrieval: dict[str, Any] | None = None,
) -> dict[str, Any]:
    journey_id, _, state = require_journey(vault)
    if authority not in AUTHORITY_LEVELS:
        raise KongziError(f"authority 必须是：{', '.join(sorted(AUTHORITY_LEVELS))}")
    source_id = new_id("src")
    source = {
        "id": source_id,
        "journey_id": journey_id,
        "title": title,
        "origin": origin,
        "kind": source_kind,
        "authority": authority,
        "author": author,
        "published_at": published_at,
        "accessed_at": iso(),
        "sha256": raw_hash,
        "characters": len(text),
        "retrieval": retrieval or {},
        "status": "registered",
    }
    state.setdefault("sources", {})[source_id] = source
    vault.save_state(state)
    source_dir = vault.notes / "Sources"
    content_path = source_dir / f"{source_id}.md"
    frontmatter = textwrap.dedent(
        f"""\
        ---
        source_id: {source_id}
        title: {json.dumps(title, ensure_ascii=False)}
        origin: {json.dumps(origin, ensure_ascii=False)}
        authority: {authority}
        accessed_at: {source["accessed_at"]}
        sha256: {raw_hash}
        ---

        # {title}

        {text.strip()}
        """
    )
    content_path.write_text(frontmatter, encoding="utf-8")
    source["content_path"] = str(content_path)
    state = vault.state()
    state["sources"][source_id] = source
    vault.save_state(state)
    event = vault.event("source.registered", source, journey_id)
    return {"source": source, "event_id": event["id"]}


def add_source(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    path = Path(args.path).expanduser().resolve()
    text, raw, detected_kind = extract_local(path)
    result = persist_source(
        vault,
        args.title or path.stem,
        text,
        sha256_bytes(raw),
        str(path),
        args.kind or detected_kind,
        args.authority,
        args.published_at,
        args.author,
    )
    emit(result)


def fetch_source(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    parsed = urllib.parse.urlparse(args.url)
    if parsed.scheme not in {"http", "https"}:
        raise KongziError("只允许 http/https URL")
    raw, final_url, content_type, charset, status = retrieve_url(
        args.url,
        timeout=args.timeout,
        max_bytes=args.max_bytes,
    )
    if content_type not in {
        "text/html",
        "text/plain",
        "application/xhtml+xml",
        "application/pdf",
    }:
        raise KongziError(f"网页内容类型不支持：{content_type}；请先下载为本地文件")
    title = args.title
    if content_type == "application/pdf":
        text = extract_pdf(raw)
        title = title or Path(parsed.path).stem or parsed.netloc
    elif content_type in {"text/html", "application/xhtml+xml"}:
        decoded = raw.decode(charset, errors="replace")
        parser = TextExtractor()
        parser.feed(decoded)
        text = parser.text()
        title = title or parser.title
    else:
        text = raw.decode(charset, errors="replace")
    title = title or parsed.netloc
    result = persist_source(
        vault,
        title,
        text,
        sha256_bytes(raw),
        final_url,
        "web",
        args.authority,
        args.published_at,
        args.author,
        {
            "requested_url": args.url,
            "final_url": final_url,
            "http_status": status,
            "content_type": content_type,
        },
    )
    emit(result)


def retrieve_url(
    url: str,
    timeout: int,
    max_bytes: int,
) -> tuple[bytes, str, str, str, int]:
    user_agent = "Kongzi-AI-Mentor/1.0 (+https://github.com/atlax-tech/kongzi-ai-mentor-skills)"
    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    errors = []
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read(max_bytes + 1)
                if len(raw) > max_bytes:
                    raise KongziError(f"网页超过 {max_bytes} 字节限制")
                return (
                    raw,
                    response.geturl(),
                    response.headers.get_content_type(),
                    response.headers.get_content_charset() or "utf-8",
                    response.status,
                )
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            errors.append(f"urllib attempt {attempt + 1}: {exc}")
            if attempt < 2:
                time.sleep(0.5 * (attempt + 1))
    curl = shutil.which("curl")
    if curl:
        with tempfile.TemporaryDirectory(prefix="kongzi-fetch-") as raw_temp:
            output = Path(raw_temp) / "body"
            completed = subprocess.run(
                [
                    curl,
                    "--location",
                    "--fail-with-body",
                    "--silent",
                    "--show-error",
                    "--max-time",
                    str(timeout),
                    "--max-filesize",
                    str(max_bytes),
                    "--user-agent",
                    user_agent,
                    "--output",
                    str(output),
                    "--write-out",
                    "%{url_effective}\\n%{http_code}\\n%{content_type}\\n",
                    url,
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            if completed.returncode == 0 and output.exists():
                raw = output.read_bytes()
                if len(raw) > max_bytes:
                    raise KongziError(f"网页超过 {max_bytes} 字节限制")
                metadata = completed.stdout.splitlines()
                final_url = metadata[0] if metadata else url
                status = int(metadata[1]) if len(metadata) > 1 and metadata[1].isdigit() else 200
                header_content_type = metadata[2] if len(metadata) > 2 else "text/html"
                media_type = header_content_type.split(";", 1)[0].strip().lower()
                charset_match = re.search(r"charset=([^;\s]+)", header_content_type, re.I)
                charset = charset_match.group(1).strip("\"'") if charset_match else "utf-8"
                return raw, final_url, media_type, charset, status
            errors.append(f"curl: {completed.stderr.strip() or completed.stdout.strip()}")
    raise KongziError("抓取失败：" + " | ".join(errors))


def list_sources(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    journey_id, _, state = require_journey(vault)
    sources = [s for s in state.get("sources", {}).values() if s["journey_id"] == journey_id]
    emit({"journey_id": journey_id, "sources": sources})


def add_claim(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    journey_id, _, state = require_journey(vault)
    source = state.get("sources", {}).get(args.source_id)
    if not source or source["journey_id"] != journey_id:
        raise KongziError(f"当前旅程中不存在来源：{args.source_id}")
    if not args.locator.strip():
        raise KongziError("事实主张必须提供可回查 locator（页码、章节、段落或时间码）")
    if not 0 <= args.confidence <= 1:
        raise KongziError("confidence 必须在 0 到 1 之间")
    claim_id = new_id("clm")
    claim = {
        "id": claim_id,
        "journey_id": journey_id,
        "statement": args.statement,
        "source_id": args.source_id,
        "locator": args.locator,
        "confidence": args.confidence,
        "status": args.status,
        "created_at": iso(),
    }
    state.setdefault("claims", {})[claim_id] = claim
    vault.save_state(state)
    event = vault.event("claim.added", claim, journey_id)
    emit({"claim": claim, "event_id": event["id"]})


def add_node(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    journey_id, _, state = require_journey(vault)
    if args.knowledge_type not in KNOWLEDGE_TYPES:
        raise KongziError(f"knowledge-type 必须是：{', '.join(sorted(KNOWLEDGE_TYPES))}")
    if not args.claim:
        raise KongziError("知识节点必须至少关联一个带来源定位符的 claim")
    for prereq in args.prerequisite:
        if prereq not in state.get("nodes", {}):
            raise KongziError(f"前置节点不存在：{prereq}")
    for claim_id in args.claim:
        claim = state.get("claims", {}).get(claim_id)
        if not claim or claim["journey_id"] != journey_id:
            raise KongziError(f"当前旅程中不存在主张：{claim_id}")
    criterion = dict(DEFAULT_MASTERY_CRITERIA[args.knowledge_type])
    if args.mastery_threshold is not None:
        if not 0 <= args.mastery_threshold <= 1:
            raise KongziError("mastery-threshold 必须在 0 到 1 之间")
        criterion["threshold"] = args.mastery_threshold
    if args.delayed_passes is not None:
        if args.delayed_passes < 1:
            raise KongziError("delayed-passes 必须至少为 1")
        criterion["delayed_passes"] = args.delayed_passes
    node_id = new_id("node")
    node = {
        "id": node_id,
        "journey_id": journey_id,
        "title": args.title,
        "knowledge_type": args.knowledge_type,
        "prerequisites": args.prerequisite,
        "claim_ids": args.claim,
        "outcome": args.outcome,
        "difficulty": args.difficulty,
        "status": "unseen",
        "mastery_criterion": criterion,
        "mastery": {
            "level": 0,
            "immediate_score": None,
            "delayed_scores": [],
            "application_passed": False,
        },
        "created_at": iso(),
        "updated_at": iso(),
    }
    state.setdefault("nodes", {})[node_id] = node
    vault.save_state(state)
    event = vault.event("node.added", node, journey_id)
    emit({"node": node, "event_id": event["id"]})


def journey_nodes(state: dict[str, Any], journey_id: str) -> list[dict[str, Any]]:
    return [n for n in state.get("nodes", {}).values() if n["journey_id"] == journey_id]


def topo_sort(nodes: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {node["id"]: node for node in nodes}
    visiting: set[str] = set()
    visited: set[str] = set()
    ordered: list[dict[str, Any]] = []

    def visit(node_id: str) -> None:
        if node_id in visited:
            return
        if node_id in visiting:
            raise KongziError(f"知识图谱存在循环依赖，涉及节点：{node_id}")
        visiting.add(node_id)
        for prereq in by_id[node_id].get("prerequisites", []):
            if prereq in by_id:
                visit(prereq)
        visiting.remove(node_id)
        visited.add(node_id)
        ordered.append(by_id[node_id])

    for identifier in by_id:
        visit(identifier)
    return ordered


def render_map(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    journey_id, journey, state = require_journey(vault)
    nodes = topo_sort(journey_nodes(state, journey_id))
    if not nodes:
        raise KongziError("当前旅程还没有知识节点")
    lines = [
        f"# {journey['goal']} · 知识地图",
        "",
        "```mermaid",
        "flowchart TD",
    ]
    for node in nodes:
        safe_title = node["title"].replace('"', "'")
        lines.append(f'  {node["id"]}["{safe_title}<br/>{node["knowledge_type"]} · {node["status"]}"]')
    for node in nodes:
        for prereq in node.get("prerequisites", []):
            if prereq in {n["id"] for n in nodes}:
                lines.append(f"  {prereq} --> {node['id']}")
    lines.extend(["```", "", "## 节点清单", ""])
    for index, node in enumerate(nodes, start=1):
        lines.append(
            f"{index}. **{node['title']}** · {node['knowledge_type']} · "
            f"目标：{node['outcome']} · 状态：{node['status']}"
        )
    path = vault.notes / "Journeys" / journey["slug"] / "Knowledge Map.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    event = vault.event("map.rendered", {"path": str(path), "node_count": len(nodes)}, journey_id)
    emit({"path": str(path), "nodes": len(nodes), "event_id": event["id"]})


def build_plan(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    if args.weeks <= 0 or args.sessions_per_week <= 0 or args.minutes <= 0:
        raise KongziError("weeks、sessions-per-week、minutes 必须大于 0")
    journey_id, journey, state = require_journey(vault)
    nodes = topo_sort(journey_nodes(state, journey_id))
    if not nodes:
        raise KongziError("先从来源材料构建知识节点，再生成计划")
    start = dt.date.fromisoformat(args.start_date) if args.start_date else local_now(vault).date()
    session_count = max(args.weeks * args.sessions_per_week, len(nodes))
    sessions: list[dict[str, Any]] = []
    for index in range(session_count):
        node = nodes[min(index, len(nodes) - 1)]
        week = index // args.sessions_per_week
        within_week = index % args.sessions_per_week
        offset = week * 7 + round(within_week * 6 / max(args.sessions_per_week - 1, 1))
        date = start + dt.timedelta(days=offset)
        mode = "learn" if index < len(nodes) else "integrate"
        sessions.append(
            {
                "sequence": index + 1,
                "date": date.isoformat(),
                "node_id": node["id"],
                "node_title": node["title"],
                "mode": mode,
                "minutes": args.minutes,
                "required_output": node["outcome"],
                "status": "planned",
            }
        )
    plan_id = new_id("plan")
    plan = {
        "id": plan_id,
        "journey_id": journey_id,
        "start_date": start.isoformat(),
        "weeks": args.weeks,
        "sessions_per_week": args.sessions_per_week,
        "minutes_per_session": args.minutes,
        "sessions": sessions,
        "created_at": iso(),
        "status": "active",
    }
    state.setdefault("plans", {})[plan_id] = plan
    state["journeys"][journey_id]["status"] = "planned"
    state["journeys"][journey_id]["active_plan_id"] = plan_id
    vault.save_state(state)
    lines = [
        f"# {journey['goal']} · 学习计划",
        "",
        f"- 周期：{args.weeks} 周",
        f"- 节奏：每周 {args.sessions_per_week} 次，每次 {args.minutes} 分钟",
        "- 规则：每次先闭卷输出，评分后纠错；到期复习优先于新内容。",
        "",
        "| # | 日期 | 节点 | 模式 | 必须产出 |",
        "|---:|---|---|---|---|",
    ]
    for item in sessions:
        lines.append(
            f"| {item['sequence']} | {item['date']} | {md_escape(item['node_title'])} | "
            f"{item['mode']} | {md_escape(item['required_output'])} |"
        )
    path = vault.notes / "Journeys" / journey["slug"] / "Learning Plan.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    event = vault.event(
        "plan.created",
        {"plan": plan, "path": str(path)},
        journey_id,
    )
    emit({"plan": plan, "path": str(path), "event_id": event["id"]})


def start_session(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    journey_id, _, state = require_journey(vault)
    node = state.get("nodes", {}).get(args.node_id)
    if not node or node["journey_id"] != journey_id:
        raise KongziError(f"当前旅程中不存在节点：{args.node_id}")
    due = due_cards(vault, journey_id)
    journey = state["journeys"][journey_id]
    active_plan_id = journey.get("active_plan_id")
    plan_item = None
    if active_plan_id and active_plan_id in state.get("plans", {}):
        plan = state["plans"][active_plan_id]
        for candidate in plan.get("sessions", []):
            if candidate["status"] == "planned" and candidate["node_id"] == args.node_id:
                candidate["status"] = "in_progress"
                plan_item = candidate
                break
    session_id = new_id("ses")
    session = {
        "id": session_id,
        "journey_id": journey_id,
        "node_id": args.node_id,
        "mode": args.mode,
        "status": "active",
        "started_at": iso(),
        "finished_at": None,
        "answer_ids": [],
        "grade_ids": [],
        "minutes": None,
        "reflection": None,
        "plan_id": active_plan_id if plan_item else None,
        "plan_sequence": plan_item["sequence"] if plan_item else None,
    }
    state.setdefault("sessions", {})[session_id] = session
    state["nodes"][args.node_id]["status"] = "learning"
    vault.save_state(state)
    event = vault.event("session.started", session, journey_id)
    emit(
        {
            "session": session,
            "due_reviews": due,
            "instruction": "若有到期复习，先复习；每道题必须等待用户作答后才能评分或讲解。",
            "event_id": event["id"],
        }
    )


def record_answer(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    journey_id, _, state = require_journey(vault)
    session = state.get("sessions", {}).get(args.session_id)
    if not session or session["journey_id"] != journey_id:
        raise KongziError(f"当前旅程中不存在会话：{args.session_id}")
    if session["status"] != "active":
        raise KongziError("只能向 active 会话记录作答")
    if args.kind not in QUESTION_KINDS:
        raise KongziError(f"kind 必须是：{', '.join(sorted(QUESTION_KINDS))}")
    if not args.answer.strip():
        raise KongziError("用户作答不能为空；Agent 不得代替用户输出")
    answer_id = new_id("ans")
    answer = {
        "id": answer_id,
        "journey_id": journey_id,
        "session_id": args.session_id,
        "node_id": session["node_id"],
        "kind": args.kind,
        "question": args.question,
        "answer": args.answer,
        "answered_at": iso(),
        "grade_id": None,
    }
    state.setdefault("answers", {})[answer_id] = answer
    state["sessions"][args.session_id]["answer_ids"].append(answer_id)
    vault.save_state(state)
    event = vault.event("answer.recorded", answer, journey_id)
    emit({"answer": answer, "event_id": event["id"], "next": f"session grade --answer-id {answer_id}"})


def schedule_card(
    vault: Vault,
    state: dict[str, Any],
    answer: dict[str, Any],
    score: float,
    claim_ids: list[str],
) -> dict[str, Any]:
    queue = vault.queue()
    card_id = f"card_{answer['node_id']}"
    existing = queue.setdefault("cards", {}).get(card_id, {})
    repetitions = existing.get("repetitions", 0)
    if score < 0.6:
        repetitions = 0
        interval = 1
    else:
        interval = REVIEW_INTERVALS[min(repetitions, len(REVIEW_INTERVALS) - 1)]
        repetitions += 1
    due_at = now() + dt.timedelta(days=interval)
    card = {
        "id": card_id,
        "journey_id": answer["journey_id"],
        "node_id": answer["node_id"],
        "prompt": answer["question"],
        "answer_evidence_id": answer["id"],
        "claim_ids": claim_ids,
        "repetitions": repetitions,
        "interval_days": interval,
        "due_at": iso(due_at),
        "last_score": score,
        "last_reviewed_at": iso(),
        "status": "scheduled",
        "history": existing.get("history", []),
    }
    queue["cards"][card_id] = card
    vault.save_queue(queue)
    return card


def grade_answer(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    journey_id, _, state = require_journey(vault)
    answer = state.get("answers", {}).get(args.answer_id)
    if not answer or answer["journey_id"] != journey_id:
        raise KongziError(f"当前旅程中不存在作答：{args.answer_id}")
    if answer.get("grade_id"):
        raise KongziError(f"该作答已经评分：{answer['grade_id']}")
    if not 0 <= args.score <= 1:
        raise KongziError("score 必须在 0 到 1 之间")
    if not all(0 <= value <= 1 for value in (args.retrieval, args.accuracy, args.transfer)):
        raise KongziError("retrieval、accuracy、transfer 必须在 0 到 1 之间")
    if not args.claim:
        raise KongziError("评分必须至少引用一个带来源定位符的 claim")
    for claim_id in args.claim:
        claim = state.get("claims", {}).get(claim_id)
        if not claim or claim["journey_id"] != journey_id:
            raise KongziError(f"评分引用的主张不存在：{claim_id}")
    grade_id = new_id("grd")
    grade = {
        "id": grade_id,
        "journey_id": journey_id,
        "answer_id": args.answer_id,
        "node_id": answer["node_id"],
        "score": args.score,
        "feedback": args.feedback,
        "correction": args.correction,
        "claim_ids": args.claim,
        "graded_at": iso(),
        "rubric": {
            "retrieval": args.retrieval,
            "accuracy": args.accuracy,
            "transfer": args.transfer,
        },
    }
    state.setdefault("grades", {})[grade_id] = grade
    state["answers"][args.answer_id]["grade_id"] = grade_id
    state["sessions"][answer["session_id"]]["grade_ids"].append(grade_id)
    node = state["nodes"][answer["node_id"]]
    node["mastery"]["immediate_score"] = args.score
    criterion = node.get("mastery_criterion", DEFAULT_MASTERY_CRITERIA[node["knowledge_type"]])
    if answer["kind"] in {"compare", "application", "debug", "create"} and args.score >= criterion["threshold"]:
        node["mastery"]["application_passed"] = True
    card = schedule_card(vault, state, answer, args.score, args.claim)
    recompute_mastery(node)
    node["updated_at"] = iso()
    vault.save_state(state)
    event = vault.event("answer.graded", grade, journey_id)
    vault.event("review.scheduled", {"card": card}, journey_id)
    emit({"grade": grade, "review_card": card, "node_status": node["status"], "event_id": event["id"]})


def recompute_mastery(node: dict[str, Any]) -> None:
    mastery = node["mastery"]
    criterion = node.get(
        "mastery_criterion",
        DEFAULT_MASTERY_CRITERIA.get(
            node.get("knowledge_type", "concept"),
            DEFAULT_MASTERY_CRITERIA["concept"],
        ),
    )
    delayed = mastery.get("delayed_scores", [])
    required_passes = int(criterion["delayed_passes"])
    threshold = float(criterion["threshold"])
    recent_delayed = delayed[-required_passes:]
    application_ok = not criterion.get("requires_application", True) or mastery.get("application_passed")
    if (
        len(recent_delayed) >= required_passes
        and all(item["score"] >= threshold for item in recent_delayed)
        and application_ok
    ):
        mastery["level"] = 4
        node["status"] = "mastered"
    elif delayed and delayed[-1]["score"] >= threshold:
        mastery["level"] = max(mastery.get("level", 0), 3)
        node["status"] = "reviewing"
    elif (mastery.get("immediate_score") or 0) >= threshold:
        mastery["level"] = max(mastery.get("level", 0), 2)
        node["status"] = "reviewing"
    else:
        mastery["level"] = max(mastery.get("level", 0), 1)
        node["status"] = "learning"


def finish_session(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    journey_id, _, state = require_journey(vault)
    session = state.get("sessions", {}).get(args.session_id)
    if not session or session["journey_id"] != journey_id:
        raise KongziError(f"当前旅程中不存在会话：{args.session_id}")
    if session["status"] != "active":
        raise KongziError("会话并非 active")
    if not 0 <= args.confidence <= 1:
        raise KongziError("confidence 必须在 0 到 1 之间")
    if not session["answer_ids"]:
        raise KongziError("会话必须至少记录一次用户输出，不能只有 Agent 讲解")
    ungraded = [aid for aid in session["answer_ids"] if not state["answers"][aid].get("grade_id")]
    if ungraded:
        raise KongziError(f"会话仍有未评分作答：{', '.join(ungraded)}")
    session.update(
        {
            "status": "finished",
            "finished_at": iso(),
            "minutes": args.minutes,
            "reflection": args.reflection,
            "confidence": args.confidence,
        }
    )
    plan_id = session.get("plan_id")
    sequence = session.get("plan_sequence")
    if plan_id and sequence and plan_id in state.get("plans", {}):
        for item in state["plans"][plan_id].get("sessions", []):
            if item["sequence"] == sequence:
                item["status"] = "completed"
                item["session_id"] = session["id"]
                item["completed_at"] = session["finished_at"]
                break
    vault.save_state(state)
    event = vault.event("session.finished", session, journey_id)
    emit({"session": session, "event_id": event["id"], "next": "review due"})


def due_cards(vault: Vault, journey_id: str | None = None) -> list[dict[str, Any]]:
    queue = vault.queue()
    current = now()
    cards = []
    for card in queue.get("cards", {}).values():
        if journey_id and card["journey_id"] != journey_id:
            continue
        if card.get("status") == "suspended":
            continue
        if parse_datetime(card["due_at"]) <= current:
            cards.append(card)
    return sorted(cards, key=lambda item: item["due_at"])


def show_due(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    journey_id = active_journey_id(vault)
    cards = due_cards(vault, journey_id if not args.all_journeys else None)
    emit(
        {
            "due_count": len(cards),
            "cards": cards,
            "instruction": "逐卡提问并等待用户回答；不要在提问时泄露答案或原始作答。",
        }
    )


def review_answer(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    journey_id, _, state = require_journey(vault)
    queue = vault.queue()
    card = queue.get("cards", {}).get(args.card_id)
    if not card or card["journey_id"] != journey_id:
        raise KongziError(f"当前旅程中不存在复习卡：{args.card_id}")
    if not 0 <= args.score <= 1:
        raise KongziError("score 必须在 0 到 1 之间")
    if not args.answer.strip():
        raise KongziError("复习作答不能为空")
    if parse_datetime(card["due_at"]) > now() and not args.allow_early:
        raise KongziError(f"复习卡尚未到期：{card['due_at']}；如确需提前练习，显式传入 --allow-early")
    history_item = {
        "id": new_id("rev"),
        "at": iso(),
        "answer": args.answer,
        "score": args.score,
        "feedback": args.feedback,
        "previous_due_at": card["due_at"],
    }
    if args.score < 0.6:
        card["repetitions"] = 0
        interval = 1
    else:
        repetitions = card.get("repetitions", 0)
        interval = REVIEW_INTERVALS[min(repetitions, len(REVIEW_INTERVALS) - 1)]
        card["repetitions"] = repetitions + 1
    card["interval_days"] = interval
    card["due_at"] = iso(now() + dt.timedelta(days=interval))
    card["last_score"] = args.score
    card["last_reviewed_at"] = iso()
    card.setdefault("history", []).append(history_item)
    queue["cards"][args.card_id] = card
    node = state["nodes"].get(card["node_id"])
    if node:
        node["mastery"].setdefault("delayed_scores", []).append(
            {"review_id": history_item["id"], "score": args.score, "at": history_item["at"]}
        )
        recompute_mastery(node)
        node["updated_at"] = iso()
    vault.save_queue(queue)
    vault.save_state(state)
    event = vault.event(
        "review.answered",
        {
            "card_id": args.card_id,
            **history_item,
            "next_due_at": card["due_at"],
            "card": card,
        },
        journey_id,
    )
    emit(
        {
            "review": history_item,
            "next_due_at": card["due_at"],
            "node_status": node["status"] if node else None,
            "event_id": event["id"],
        }
    )


def snooze_review(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    if args.hours <= 0:
        raise KongziError("hours 必须大于 0")
    queue = vault.queue()
    card = queue.get("cards", {}).get(args.card_id)
    if not card:
        raise KongziError(f"复习卡不存在：{args.card_id}")
    old_due = card["due_at"]
    card["due_at"] = iso(now() + dt.timedelta(hours=args.hours))
    vault.save_queue(queue)
    event = vault.event(
        "review.snoozed",
        {"card_id": args.card_id, "old_due_at": old_due, "new_due_at": card["due_at"]},
        card["journey_id"],
    )
    emit({"card_id": args.card_id, "due_at": card["due_at"], "event_id": event["id"]})


def capture_note(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    journey_id, journey, state = require_journey(vault)
    note_id = new_id("note")
    note = {
        "id": note_id,
        "journey_id": journey_id,
        "title": args.title,
        "body": args.body,
        "claim_ids": args.claim,
        "created_at": iso(),
    }
    for claim_id in args.claim:
        if claim_id not in state.get("claims", {}):
            raise KongziError(f"主张不存在：{claim_id}")
    state.setdefault("notes", {})[note_id] = note
    vault.save_state(state)
    path = vault.notes / "Journeys" / journey["slug"] / "Notes" / f"{slugify(args.title)}-{note_id[-6:]}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    citations = "\n".join(f"- `{claim_id}`" for claim_id in args.claim) or "- 无（个人反思/待核验）"
    path.write_text(
        f"# {args.title}\n\n{args.body}\n\n## 证据主张\n\n{citations}\n",
        encoding="utf-8",
    )
    event = vault.event(
        "note.captured",
        {"note": note, "path": str(path)},
        journey_id,
    )
    emit({"note": note, "path": str(path), "event_id": event["id"]})


def period_bounds(
    kind: str,
    date_value: str | None,
    timezone: ZoneInfo,
) -> tuple[dt.datetime, dt.datetime, str]:
    target = dt.date.fromisoformat(date_value) if date_value else now().astimezone(timezone).date()
    if kind == "daily":
        start_date = target
        end_date = target + dt.timedelta(days=1)
        label = target.isoformat()
    else:
        start_date = target - dt.timedelta(days=target.weekday())
        end_date = start_date + dt.timedelta(days=7)
        label = f"{start_date.isoformat()}--{(end_date - dt.timedelta(days=1)).isoformat()}"
    start = dt.datetime.combine(start_date, dt.time.min, tzinfo=timezone).astimezone(UTC)
    end = dt.datetime.combine(end_date, dt.time.min, tzinfo=timezone).astimezone(UTC)
    return start, end, label


def generate_report(args: argparse.Namespace, emit_result: bool = True) -> dict[str, Any]:
    vault = Vault(Path(args.vault))
    journey_id, journey, state = require_journey(vault)
    start, end, label = period_bounds(args.kind, args.date, vault_timezone(vault))
    events = [
        event
        for event in vault.events()
        if event.get("journey_id") == journey_id
        and start <= parse_datetime(event["at"]) < end
    ]
    sessions = [
        event["payload"] for event in events if event["type"] == "session.finished"
    ]
    grades = [event["payload"] for event in events if event["type"] == "answer.graded"]
    reviews = [event["payload"] for event in events if event["type"] == "review.answered"]
    minutes = sum(item.get("minutes") or 0 for item in sessions)
    scores = [float(item["score"]) for item in grades] + [float(item["score"]) for item in reviews]
    average = round(sum(scores) / len(scores), 3) if scores else None
    weak = sorted(
        (
            {
                "node_id": node["id"],
                "title": node["title"],
                "level": node["mastery"]["level"],
                "status": node["status"],
            }
            for node in journey_nodes(state, journey_id)
            if node["status"] != "mastered"
        ),
        key=lambda item: item["level"],
    )
    due = due_cards(vault, journey_id)
    overdue_plan = []
    plan_id = journey.get("active_plan_id")
    plan = state.get("plans", {}).get(plan_id)
    if plan:
        local_date = local_now(vault).date()
        overdue_plan = [
            item
            for item in plan.get("sessions", [])
            if item["status"] == "planned" and dt.date.fromisoformat(item["date"]) < local_date
        ]
    if due:
        next_move = f"先完成 {len(due)} 张到期复习卡"
    elif overdue_plan:
        next_move = f"补做逾期会话：{overdue_plan[0]['node_title']}"
    else:
        next_move = f"继续节点：{weak[0]['title']}" if weak else "做一个综合迁移项目"
    report = {
        "schema_version": SCHEMA_VERSION,
        "kind": args.kind,
        "period": label,
        "generated_at": iso(),
        "journey_id": journey_id,
        "journey_goal": journey["goal"],
        "minutes": minutes,
        "sessions_finished": len(sessions),
        "answers_graded": len(grades),
        "reviews_completed": len(reviews),
        "average_score": average,
        "due_reviews": len(due),
        "overdue_planned_sessions": len(overdue_plan),
        "not_mastered": weak,
        "next_move": next_move,
        "evidence_event_ids": [event["id"] for event in events],
    }
    directory = vault.notes / "Reports" / ("Daily" if args.kind == "daily" else "Weekly")
    report_id = new_id("report")
    path = directory / f"{label}--{report_id[-6:]}.md"
    rows = "\n".join(
        f"- {item['title']} · Level {item['level']} · {item['status']}" for item in weak[:8]
    ) or "- 暂无"
    path.write_text(
        textwrap.dedent(
            f"""\
            # Kongzi {args.kind.title()} Report · {label}

            ## 本周期

            - 学习时长：{minutes} 分钟
            - 完成会话：{len(sessions)}
            - 已评分输出：{len(grades)}
            - 延迟复习：{len(reviews)}
            - 平均得分：{average if average is not None else "暂无"}
            - 当前到期复习：{len(due)}
            - 逾期计划会话：{len(overdue_plan)}

            ## 尚未掌握

            {rows}

            ## 唯一下一步

            {next_move}

            ## 证据事件

            {chr(10).join(f"- `{event['id']}` · {event['type']}" for event in events) or "- 本周期无事件"}
            """
        ),
        encoding="utf-8",
    )
    event = vault.event("report.generated", {"kind": args.kind, "period": label, "path": str(path)}, journey_id)
    result = {"report": report, "path": str(path), "event_id": event["id"]}
    if emit_result:
        emit(result)
    return result


def auto_reports(vault: Vault) -> list[dict[str, Any]]:
    if not active_journey_id(vault):
        return []
    local_date = local_now(vault).date()
    kinds = ["daily"]
    if local_date.weekday() == 6:
        kinds.append("weekly")
    existing = {
        (event.get("payload", {}).get("kind"), event.get("payload", {}).get("period"))
        for event in vault.events()
        if event.get("type") == "report.generated"
    }
    created = []
    for kind in kinds:
        _, _, label = period_bounds(kind, local_date.isoformat(), vault_timezone(vault))
        if (kind, label) in existing:
            continue
        created.append(
            generate_report(
                argparse.Namespace(vault=str(vault.root), kind=kind, date=local_date.isoformat()),
                emit_result=False,
            )
        )
    return created


def generate_auto_reports(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    vault.require()
    created = auto_reports(vault)
    emit({"created": created, "created_count": len(created)})


def set_mentor(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    state = vault.state()
    source = Path(args.persona_path).expanduser().resolve()
    if not source.exists():
        raise KongziError(f"导师人格文件不存在：{source}")
    destination = vault.notes / "Mentors" / f"{slugify(args.name)}.md"
    destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    state["mentor"] = {
        "enabled": True,
        "name": args.name,
        "persona_path": str(destination),
        "source_path": str(source),
        "set_at": iso(),
        "boundary": "persona-controls-style-and-models; evidence-controls-facts",
    }
    vault.save_state(state)
    event = vault.event("mentor.enabled", state["mentor"])
    emit({"mentor": state["mentor"], "event_id": event["id"]})


def disable_mentor(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    state = vault.state()
    state["mentor"]["enabled"] = False
    state["mentor"]["disabled_at"] = iso()
    vault.save_state(state)
    event = vault.event("mentor.disabled", {})
    emit({"mentor": state["mentor"], "event_id": event["id"]})


def skill_search_roots(vault: Vault) -> list[Path]:
    roots: list[Path] = []
    env = os.environ.get("KONGZI_SKILLS_DIRS", "")
    roots.extend(Path(item).expanduser() for item in env.split(os.pathsep) if item)
    roots.extend(
        [
            vault.root / ".claude" / "skills",
            vault.root / ".codex" / "skills",
            Path.home() / ".claude" / "skills",
            Path.home() / ".codex" / "skills",
            Path.home() / ".cursor" / "skills",
            Path.home() / ".agents" / "skills",
        ]
    )
    unique: list[Path] = []
    seen = set()
    for root in roots:
        resolved = root.expanduser().resolve()
        if str(resolved) not in seen:
            seen.add(str(resolved))
            unique.append(resolved)
    return unique


INTEGRATION_NAMES = {
    "cangjie": ("cangjie-skill",),
    "nuwa": ("nuwa-skill", "huashu-nuwa"),
    "darwin": ("darwin-skill",),
    "video-downloader": ("video-downloader",),
}


def discover_integrations(vault: Vault) -> dict[str, Any]:
    result: dict[str, Any] = {}
    roots = skill_search_roots(vault)
    for integration, names in INTEGRATION_NAMES.items():
        found = None
        for root in roots:
            for name in names:
                candidate = root / name
                if (candidate / "SKILL.md").exists():
                    found = candidate
                    break
            if found:
                break
        provenance = None
        if found and (found / "UPSTREAM.json").exists():
            provenance = json_load(found / "UPSTREAM.json", {})
        elif found and (found / ".git").exists():
            completed = subprocess.run(
                ["git", "-C", str(found), "rev-parse", "HEAD"],
                check=False,
                capture_output=True,
                text=True,
            )
            if completed.returncode == 0:
                provenance = {"revision": completed.stdout.strip()}
        result[integration] = {
            "installed": bool(found),
            "path": str(found) if found else None,
            "provenance": provenance,
            "searched": [str(root) for root in roots],
        }
    return result


def integration_status(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    vault.require()
    emit({"integrations": discover_integrations(vault)})


def prepare_integration(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    journey_id, journey, state = require_journey(vault)
    available = discover_integrations(vault)
    if args.integration not in available:
        raise KongziError(f"未知集成：{args.integration}")
    if not available[args.integration]["installed"]:
        raise KongziError(
            f"{args.integration} 尚未安装；运行 python3 scripts/install_integrations.py --target <skills-dir>"
        )
    run_id = new_id("run")
    run_dir = vault.meta / "integrations" / args.integration / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    sources = [
        item for item in state.get("sources", {}).values() if item["journey_id"] == journey_id
    ]
    request = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "integration": args.integration,
        "journey": journey,
        "sources": sources,
        "output_dir": str(run_dir / "output"),
        "created_at": iso(),
        "instructions": integration_instructions(args.integration),
        "upstream": available[args.integration].get("provenance"),
    }
    request_path = run_dir / "request.json"
    json_write(request_path, request)
    registry = json_load(vault.integrations_path, {"schema_version": SCHEMA_VERSION, "runs": {}})
    registry.setdefault("runs", {})[run_id] = {
        "id": run_id,
        "integration": args.integration,
        "status": "prepared",
        "request_path": str(request_path),
        "output_dir": request["output_dir"],
        "created_at": iso(),
    }
    json_write(vault.integrations_path, registry)
    event = vault.event("integration.prepared", registry["runs"][run_id], journey_id)
    emit(
        {
            "run": registry["runs"][run_id],
            "skill_path": available[args.integration]["path"],
            "agent_instruction": request["instructions"],
            "event_id": event["id"],
        }
    )


def integration_instructions(name: str) -> str:
    if name == "cangjie":
        return (
            "Read the installed cangjie-skill/SKILL.md completely. Run its full five-phase "
            "distillation workflow over every registered source, preserving metadata, source "
            "locators, verified/rejected claims, atomic skills, glossary, digest, and test prompts. "
            "Write the complete output to output_dir; do not summarize from memory."
        )
    if name == "nuwa":
        return (
            "Read the installed nuwa-skill/SKILL.md completely. Research the requested mentor with "
            "all six dimensions, prioritize primary sources above 50%, encode 3-7 decision models, "
            "provenance and honest boundaries, then write the complete persona skill to output_dir."
        )
    if name == "darwin":
        return (
            "Read the installed darwin-skill/SKILL.md completely. Evaluate Kongzi's test prompts "
            "with its nine-dimensional rubric using independent judges, retain baseline evidence, "
            "respect the ratchet and checkpoint before applying changes, and write all artifacts to output_dir."
        )
    return (
        "Read the installed video-downloader/SKILL.md completely. Download and transcribe the supplied "
        "video, preserving metadata.json, caption, audio/video paths, ASR backend, timestamps and failures "
        "in output_dir. Do not invent missing transcript segments."
    )


def import_cangjie(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    journey_id, _, state = require_journey(vault)
    output = Path(args.output_dir).expanduser().resolve()
    if not output.exists():
        raise KongziError(f"Cangjie 输出目录不存在：{output}")
    markdown_files = sorted(output.rglob("*.md"))
    if not markdown_files:
        raise KongziError("Cangjie 输出中没有 Markdown 文件")
    imported_sources = []
    imported_claims = []
    for path in markdown_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        if not text.strip():
            continue
        result = persist_source(
            vault,
            f"Cangjie · {path.stem}",
            text,
            sha256_bytes(text.encode()),
            str(path),
            "cangjie-distillation",
            "secondary",
            None,
            "cangjie-skill",
            {"integration": "cangjie", "relative_path": str(path.relative_to(output))},
        )
        imported_sources.append(result["source"]["id"])
        for match in re.finditer(
            r"(?mi)^(?:[-*]\s*)?(?:claim|主张|结论)\s*[:：]\s*(.+?)(?:\s+\[(.+?)\])?$",
            text,
        ):
            claim_id = new_id("clm")
            claim = {
                "id": claim_id,
                "journey_id": journey_id,
                "statement": match.group(1).strip(),
                "source_id": result["source"]["id"],
                "locator": match.group(2) or f"{path.name}:line-derived",
                "confidence": 0.8,
                "status": "verified-by-cangjie",
                "created_at": iso(),
            }
            state = vault.state()
            state.setdefault("claims", {})[claim_id] = claim
            vault.save_state(state)
            vault.event("claim.added", claim, journey_id)
            imported_claims.append(claim_id)
    event = vault.event(
        "integration.cangjie_imported",
        {"output_dir": str(output), "source_ids": imported_sources, "claim_ids": imported_claims},
        journey_id,
    )
    emit(
        {
            "imported_source_ids": imported_sources,
            "imported_claim_ids": imported_claims,
            "event_id": event["id"],
            "note": "未匹配到结构化 claim 的内容仍以可回查来源保留，由 Agent 人工核验后再登记主张。",
        }
    )


def import_nuwa(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    source = Path(args.persona_path).expanduser().resolve()
    if not source.exists():
        raise KongziError(f"Nuwa 人格文件不存在：{source}")
    destination = vault.notes / "Mentors" / f"{slugify(args.name)}.md"
    destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    state = vault.state()
    state["mentor"] = {
        "enabled": True,
        "name": args.name,
        "persona_path": str(destination),
        "source_path": str(source),
        "set_at": iso(),
        "integration": "nuwa",
        "boundary": "persona-controls-style-and-models; evidence-controls-facts",
    }
    vault.save_state(state)
    event = vault.event("integration.nuwa_imported", state["mentor"])
    emit({"mentor": state["mentor"], "event_id": event["id"]})


def run_video(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    journey_id, _, _ = require_journey(vault)
    integrations = discover_integrations(vault)
    video_path = integrations["video-downloader"]["path"]
    if not video_path:
        raise KongziError("video-downloader 未安装")
    script = Path(video_path) / "scripts" / "download_video.py"
    if not script.exists():
        raise KongziError(f"video-downloader 缺少脚本：{script}")
    output = Path(args.output_dir).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, str(script), args.url, "--output-dir", str(output)]
    if args.metadata_only:
        command.append("--metadata-only")
    if args.asr_backend:
        command.extend(["--asr", args.asr_backend])
    if args.asr_model:
        command.extend(["--asr-model", args.asr_model])
    if args.asr_language:
        command.extend(["--asr-language", args.asr_language])
    if args.asr_max_seconds:
        command.extend(["--asr-max-seconds", str(args.asr_max_seconds)])
    completed = subprocess.run(command, check=False, text=True, capture_output=True)
    run_record = {
        "url": args.url,
        "command": command,
        "output_dir": str(output),
        "returncode": completed.returncode,
        "stdout": completed.stdout[-8000:],
        "stderr": completed.stderr[-8000:],
    }
    event = vault.event("integration.video_ran", run_record, journey_id)
    if completed.returncode:
        raise KongziError(
            f"video-downloader 失败（事件 {event['id']}）：{completed.stderr.strip() or completed.stdout.strip()}"
        )
    transcript_candidates = (
        list(output.rglob("transcript.txt"))
        + list(output.rglob("*transcript*.md"))
        + list(output.rglob("post_caption.txt"))
    )
    registered = None
    if transcript_candidates:
        transcript = transcript_candidates[0]
        add_args = argparse.Namespace(
            vault=str(vault.root),
            path=str(transcript),
            title=args.title or f"视频转录 · {urllib.parse.urlparse(args.url).netloc}",
            kind="video-transcript" if "transcript" in transcript.name else "video-caption",
            authority=args.authority,
            published_at=None,
            author=None,
        )
        text, raw, _ = extract_local(transcript)
        registered = persist_source(
            vault,
            add_args.title,
            text,
            sha256_bytes(raw),
            args.url,
            add_args.kind,
            add_args.authority,
            None,
            None,
            {
                "integration": "video-downloader",
                "transcript_path": str(transcript),
                "output_dir": str(output),
            },
        )
    emit({"run": run_record, "registered": registered, "event_id": event["id"]})


def reminder_generate(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    vault.require()
    if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", args.time):
        raise KongziError("time 必须是 24 小时制 HH:MM")
    script = Path(__file__).resolve()
    if args.method == "launchd":
        hour, minute = (int(item) for item in args.time.split(":", 1))
        plist = textwrap.dedent(
            f"""\
            <?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
            <plist version="1.0">
            <dict>
              <key>Label</key><string>dev.kongzi.review-reminder</string>
              <key>ProgramArguments</key>
              <array>
                <string>{sys.executable}</string>
                <string>{script}</string>
                <string>reminder</string><string>notify</string>
                <string>--vault</string><string>{vault.root}</string>
                <string>--reports</string>
              </array>
              <key>StartCalendarInterval</key>
              <dict><key>Hour</key><integer>{hour}</integer><key>Minute</key><integer>{minute}</integer></dict>
              <key>StandardOutPath</key><string>{vault.meta / "reminder.log"}</string>
              <key>StandardErrorPath</key><string>{vault.meta / "reminder-error.log"}</string>
            </dict>
            </plist>
            """
        )
        path = vault.meta / "reminders" / "dev.kongzi.review-reminder.plist"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(plist, encoding="utf-8")
        install_command = f"launchctl bootstrap gui/$(id -u) {path}"
    else:
        minute, hour = (int(args.time.split(":")[1]), int(args.time.split(":")[0]))
        path = vault.meta / "reminders" / "cron.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        cron = (
            f"{minute} {hour} * * * {sys.executable} {script} reminder notify "
            f"--vault {vault.root} --reports\n"
        )
        path.write_text(cron, encoding="utf-8")
        install_command = f"(crontab -l; cat {path}) | crontab -"
    config = vault.config()
    config["reminders"] = {
        "method": args.method,
        "time": args.time,
        "installed": False,
        "definition_path": str(path),
    }
    json_write(vault.config_path, config)
    event = vault.event("reminder.generated", config["reminders"])
    emit({"definition_path": str(path), "install_command": install_command, "event_id": event["id"]})


def reminder_install(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    config = vault.config()
    reminder = config.get("reminders", {})
    path_value = reminder.get("definition_path")
    if not path_value:
        raise KongziError("先运行 reminder generate")
    path = Path(path_value)
    if reminder["method"] == "launchd":
        command = ["launchctl", "bootstrap", f"gui/{os.getuid()}", str(path)]
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
    else:
        existing = subprocess.run(["crontab", "-l"], check=False, capture_output=True, text=True)
        combined = existing.stdout + path.read_text(encoding="utf-8")
        completed = subprocess.run(["crontab", "-"], input=combined, check=False, capture_output=True, text=True)
        command = ["crontab", "-"]
    if completed.returncode:
        raise KongziError(f"提醒安装失败：{completed.stderr.strip()}")
    reminder["installed"] = True
    reminder["installed_at"] = iso()
    config["reminders"] = reminder
    json_write(vault.config_path, config)
    event = vault.event("reminder.installed", {"command": command, **reminder})
    emit({"installed": True, "method": reminder["method"], "event_id": event["id"]})


def reminder_notify(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    vault.require()
    cards = due_cards(vault)
    message = f"Kongzi：有 {len(cards)} 张复习卡到期" if cards else "Kongzi：今天没有到期复习"
    notified = False
    if cards and sys.platform == "darwin" and shutil.which("osascript"):
        safe = message.replace("\\", "\\\\").replace('"', '\\"')
        completed = subprocess.run(
            ["osascript", "-e", f'display notification "{safe}" with title "Kongzi AI Mentor"'],
            check=False,
            capture_output=True,
            text=True,
        )
        notified = completed.returncode == 0
    reports = auto_reports(vault) if args.reports else []
    event = vault.event(
        "reminder.checked",
        {"due_count": len(cards), "notified": notified, "report_paths": [item["path"] for item in reports]},
    )
    emit(
        {
            "message": message,
            "due_count": len(cards),
            "notified": notified,
            "reports_created": reports,
            "event_id": event["id"],
        }
    )


def show_status(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    config = vault.config()
    state = vault.state()
    profile = vault.profile()
    journey_id = config.get("active_journey_id")
    journey = state.get("journeys", {}).get(journey_id)
    nodes = journey_nodes(state, journey_id) if journey_id else []
    statuses: dict[str, int] = {}
    for node in nodes:
        statuses[node["status"]] = statuses.get(node["status"], 0) + 1
    active_sessions = [
        item for item in state.get("sessions", {}).values() if item["status"] == "active"
    ]
    sources = [
        item for item in state.get("sources", {}).values() if item.get("journey_id") == journey_id
    ]
    claims = [
        item for item in state.get("claims", {}).values() if item.get("journey_id") == journey_id
    ]
    due = due_cards(vault, journey_id) if journey_id else []
    overdue_plan = []
    if journey:
        plan_id = journey.get("active_plan_id")
        plan = state.get("plans", {}).get(plan_id)
        if plan:
            today = local_now(vault).date()
            overdue_plan = [
                item
                for item in plan.get("sessions", [])
                if item["status"] == "planned" and dt.date.fromisoformat(item["date"]) < today
            ]
    if not journey:
        next_action = "创建学习旅程"
    elif due:
        next_action = f"完成 {len(due)} 张到期复习卡"
    elif active_sessions:
        next_action = f"继续会话 {active_sessions[0]['id']}"
    elif len(profile.get("interviews", [])) < 6:
        next_action = "完成画像访谈"
    elif not sources:
        next_action = "录入至少一份学习资料"
    elif not claims:
        next_action = "从材料登记带定位符的权威主张"
    elif not nodes:
        next_action = "构建知识地图节点"
    elif overdue_plan:
        next_action = f"补做 {len(overdue_plan)} 个逾期计划会话，先从 {overdue_plan[0]['node_title']} 开始"
    else:
        next_action = "开始计划中的下一次学习会话"
    emit(
        {
            "vault": str(vault.root),
            "active_journey": journey,
            "profile_interview_items": len(profile.get("interviews", [])),
            "sources": len(sources),
            "claims": len(claims),
            "nodes": statuses,
            "due_reviews": len(due),
            "active_sessions": active_sessions,
            "plan_drift": {"overdue_count": len(overdue_plan), "sessions": overdue_plan[:5]},
            "mentor": state.get("mentor"),
            "reminders": config.get("reminders"),
            "next_action": next_action,
        }
    )


def copy_pre_repair(path: Path) -> str | None:
    if not path.exists():
        return None
    suffix = now().strftime("%Y%m%dT%H%M%SZ")
    backup = path.with_name(f"{path.name}.pre-repair-{suffix}")
    shutil.copy2(path, backup)
    return str(backup)


def apply_nested(target: dict[str, Any], dotted: str, value: Any) -> None:
    segments = dotted.split(".")
    current = target
    for segment in segments[:-1]:
        current = current.setdefault(segment, {})
    current[segments[-1]] = value


def rebuild_from_events(vault: Vault) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    events = vault.events()
    initialized = next((e for e in events if e["type"] == "vault.initialized"), None)
    state: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "created_at": initialized["at"] if initialized else iso(),
        "updated_at": iso(),
        "journeys": {},
        "sources": {},
        "claims": {},
        "nodes": {},
        "plans": {},
        "sessions": {},
        "answers": {},
        "grades": {},
        "notes": {},
        "mentor": {"enabled": False, "name": None, "persona_path": None},
    }
    profile: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "learner_name": (initialized or {}).get("payload", {}).get("learner_name", ""),
        "self_reported": {},
        "observed": {
            "strengths": [],
            "frictions": [],
            "preferred_formats": {},
            "calibration": [],
        },
        "interviews": [],
        "updated_at": iso(),
    }
    queue: dict[str, Any] = {"schema_version": SCHEMA_VERSION, "cards": {}, "updated_at": iso()}
    for event in events:
        kind = event["type"]
        payload = event.get("payload", {})
        if kind == "journey.created":
            state["journeys"][payload["id"]] = payload
        elif kind == "source.registered":
            state["sources"][payload["id"]] = payload
        elif kind == "claim.added":
            state["claims"][payload["id"]] = payload
        elif kind == "node.added":
            state["nodes"][payload["id"]] = payload
        elif kind == "plan.created" and payload.get("plan"):
            plan = payload["plan"]
            state["plans"][plan["id"]] = plan
            journey = state["journeys"].get(plan["journey_id"])
            if journey:
                journey["active_plan_id"] = plan["id"]
                journey["status"] = "planned"
        elif kind in {"session.started", "session.finished"}:
            state["sessions"][payload["id"]] = payload
            node = state["nodes"].get(payload.get("node_id"))
            if node and kind == "session.started":
                node["status"] = "learning"
            plan_id = payload.get("plan_id")
            sequence = payload.get("plan_sequence")
            plan = state["plans"].get(plan_id)
            if plan and sequence:
                for item in plan.get("sessions", []):
                    if item["sequence"] == sequence:
                        item["status"] = "in_progress" if kind == "session.started" else "completed"
                        if kind == "session.finished":
                            item["session_id"] = payload["id"]
                            item["completed_at"] = payload["finished_at"]
                        break
        elif kind == "answer.recorded":
            state["answers"][payload["id"]] = payload
            session = state["sessions"].get(payload["session_id"])
            if session and payload["id"] not in session.setdefault("answer_ids", []):
                session["answer_ids"].append(payload["id"])
        elif kind == "answer.graded":
            grade = payload
            state["grades"][grade["id"]] = grade
            answer = state["answers"].get(grade["answer_id"])
            if answer:
                answer["grade_id"] = grade["id"]
                session = state["sessions"].get(answer["session_id"])
                if session and grade["id"] not in session.setdefault("grade_ids", []):
                    session["grade_ids"].append(grade["id"])
                node = state["nodes"].get(answer["node_id"])
                if node:
                    node["mastery"]["immediate_score"] = grade["score"]
                    criterion = node.get(
                        "mastery_criterion",
                        DEFAULT_MASTERY_CRITERIA[node["knowledge_type"]],
                    )
                    if (
                        answer["kind"] in {"compare", "application", "debug", "create"}
                        and grade["score"] >= criterion["threshold"]
                    ):
                        node["mastery"]["application_passed"] = True
                    recompute_mastery(node)
        elif kind == "review.scheduled" and payload.get("card"):
            card = payload["card"]
            queue["cards"][card["id"]] = card
        elif kind == "review.answered" and payload.get("card"):
            card = payload["card"]
            queue["cards"][card["id"]] = card
            node = state["nodes"].get(card["node_id"])
            if node:
                node["mastery"].setdefault("delayed_scores", []).append(
                    {
                        "review_id": payload["id"],
                        "score": payload["score"],
                        "at": payload["at"],
                    }
                )
                recompute_mastery(node)
        elif kind == "note.captured" and payload.get("note"):
            state["notes"][payload["note"]["id"]] = payload["note"]
        elif kind in {"mentor.enabled", "integration.nuwa_imported"}:
            state["mentor"] = payload
        elif kind == "mentor.disabled":
            state["mentor"]["enabled"] = False
            state["mentor"]["disabled_at"] = event["at"]
        elif kind == "profile.self_reported":
            apply_nested(profile["self_reported"], payload["field"], payload["value"])
            profile["interviews"].append(payload)
        elif kind == "profile.observed":
            profile["observed"]["calibration"].append(payload)
    return state, profile, queue


def repair(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    vault.require()
    state, profile, queue = rebuild_from_events(vault)
    selected = (
        ("state", "profile", "queue")
        if args.component == "all"
        else (args.component,)
    )
    paths = {
        "state": vault.state_path,
        "profile": vault.profile_path,
        "queue": vault.queue_path,
    }
    values = {"state": state, "profile": profile, "queue": queue}
    backups = {}
    for component in selected:
        backups[component] = copy_pre_repair(paths[component])
        json_write(paths[component], values[component])
    event = vault.event(
        "recovery.completed",
        {"components": selected, "pre_repair_backups": backups, "event_count": len(vault.events())},
    )
    emit(
        {
            "repaired": selected,
            "pre_repair_backups": backups,
            "event_id": event["id"],
            "instruction": "运行 doctor 验证重建结果；pre-repair 文件保留，可人工回退。",
        }
    )


def export_bundle(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    vault.require()
    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and not args.overwrite:
        raise KongziError(f"导出文件已存在：{output}；显式传入 --overwrite 才会替换")
    include_roots = (vault.meta, vault.notes)
    files = []
    for root in include_roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix == ".tmp":
                continue
            relative = path.relative_to(vault.root)
            data = path.read_bytes()
            files.append(
                {
                    "path": relative.as_posix(),
                    "sha256": sha256_bytes(data),
                    "bytes": len(data),
                }
            )
    manifest = {
        "format": "kongzi-learning-bundle",
        "format_version": 1,
        "schema_version": SCHEMA_VERSION,
        "exported_at": iso(),
        "source_vault_name": vault.root.name,
        "active_journey_id": active_journey_id(vault),
        "files": files,
    }
    temp = output.with_suffix(output.suffix + ".tmp")
    with zipfile.ZipFile(temp, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "manifest.json",
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        )
        for item in files:
            archive.write(vault.root / item["path"], f"payload/{item['path']}")
    if output.exists():
        backup = output.with_suffix(output.suffix + ".bak")
        shutil.copy2(output, backup)
    temp.replace(output)
    event = vault.event(
        "bundle.exported",
        {"output": str(output), "sha256": sha256_bytes(output.read_bytes()), "files": len(files)},
    )
    emit(
        {
            "output": str(output),
            "sha256": sha256_bytes(output.read_bytes()),
            "files": len(files),
            "event_id": event["id"],
        }
    )


def safe_zip_member(name: str) -> bool:
    path = PurePosixPath(name)
    return not path.is_absolute() and ".." not in path.parts and path.parts not in {(), (".",)}


def rebase_imported_paths(vault: Vault) -> None:
    config = vault.config()
    config["vault_root"] = str(vault.root)
    config.setdefault("knowledge_base", {})["path"] = str(vault.root)
    config["updated_at"] = iso()
    json_write(vault.config_path, config)
    state = vault.state()
    for source in state.get("sources", {}).values():
        expected = vault.notes / "Sources" / f"{source['id']}.md"
        if expected.exists():
            source["content_path"] = str(expected)
    mentor = state.get("mentor", {})
    if mentor.get("name"):
        expected = vault.notes / "Mentors" / f"{slugify(mentor['name'])}.md"
        if expected.exists():
            mentor["persona_path"] = str(expected)
    vault.save_state(state)


def import_bundle(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    bundle = Path(args.bundle).expanduser().resolve()
    if not bundle.exists():
        raise KongziError(f"学习包不存在：{bundle}")
    if vault.config_path.exists():
        raise KongziError("目标 vault 已有 Kongzi 状态；为避免旅程串写，只能导入到未初始化 vault")
    if vault.notes.exists():
        raise KongziError("目标 vault 已有 Kongzi/ 目录；请改用新的或尚未初始化的 Obsidian vault")
    vault.root.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(bundle) as archive:
        names = archive.namelist()
        if any(not safe_zip_member(name) for name in names):
            raise KongziError("学习包包含不安全路径")
        try:
            manifest = json.loads(archive.read("manifest.json"))
        except (KeyError, json.JSONDecodeError) as exc:
            raise KongziError("学习包缺少有效 manifest.json") from exc
        if manifest.get("format") != "kongzi-learning-bundle":
            raise KongziError("不是 Kongzi learning bundle")
        if manifest.get("schema_version", 0) > SCHEMA_VERSION:
            raise KongziError(
                f"学习包 schema {manifest['schema_version']} 高于当前支持的 {SCHEMA_VERSION}"
            )
        listed = {item["path"]: item for item in manifest.get("files", [])}
        with tempfile.TemporaryDirectory(prefix="kongzi-import-") as raw_temp:
            staging = Path(raw_temp)
            for relative, item in listed.items():
                relative_path = PurePosixPath(relative)
                if (
                    not safe_zip_member(relative)
                    or not relative_path.parts
                    or relative_path.parts[0] not in {".kongzi", "Kongzi"}
                ):
                    raise KongziError(f"学习包 manifest 路径不安全：{relative}")
                member = f"payload/{relative}"
                if member not in names:
                    raise KongziError(f"学习包缺少文件：{relative}")
                data = archive.read(member)
                if sha256_bytes(data) != item["sha256"]:
                    raise KongziError(f"学习包哈希校验失败：{relative}")
                target = staging / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            for name in (".kongzi", "Kongzi"):
                source = staging / name
                if source.exists():
                    source.replace(vault.root / name)
    vault.require()
    rebase_imported_paths(vault)
    event = vault.event(
        "bundle.imported",
        {
            "bundle": str(bundle),
            "sha256": sha256_bytes(bundle.read_bytes()),
            "files": len(manifest.get("files", [])),
        },
    )
    emit(
        {
            "vault": str(vault.root),
            "files": len(manifest.get("files", [])),
            "active_journey_id": active_journey_id(vault),
            "event_id": event["id"],
        }
    )


def migrate(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    vault.require()
    paths = (
        vault.config_path,
        vault.profile_path,
        vault.state_path,
        vault.queue_path,
        vault.integrations_path,
    )
    versions = {}
    for path in paths:
        data = json_load(path, {})
        version = int(data.get("schema_version", 0))
        versions[path.name] = version
        if version > SCHEMA_VERSION:
            raise KongziError(f"{path.name} schema {version} 高于当前支持的 {SCHEMA_VERSION}")
        if version < SCHEMA_VERSION:
            raise KongziError(
                f"{path.name} schema {version} 需要专用迁移器；当前发行版没有可安全执行的路径"
            )
    emit({"up_to_date": True, "schema_version": SCHEMA_VERSION, "files": versions})


def doctor(args: argparse.Namespace) -> None:
    vault = Vault(Path(args.vault))
    vault.require()
    problems: list[str] = []
    state = vault.state()
    queue = vault.queue()
    events = vault.events()
    journey_ids = set(state.get("journeys", {}))
    for source in state.get("sources", {}).values():
        if source.get("journey_id") not in journey_ids:
            problems.append(f"来源 {source['id']} 指向未知旅程")
        path = source.get("content_path")
        if path and not Path(path).exists():
            problems.append(f"来源正文缺失：{source['id']}")
    for claim in state.get("claims", {}).values():
        if claim.get("source_id") not in state.get("sources", {}):
            problems.append(f"主张 {claim['id']} 缺少来源")
        if not claim.get("locator"):
            problems.append(f"主张 {claim['id']} 缺少定位符")
    try:
        topo_sort(state.get("nodes", {}).values())
    except KongziError as exc:
        problems.append(str(exc))
    for card in queue.get("cards", {}).values():
        if card.get("node_id") not in state.get("nodes", {}):
            problems.append(f"复习卡 {card['id']} 指向未知节点")
        try:
            parse_datetime(card["due_at"])
        except (ValueError, KeyError):
            problems.append(f"复习卡 {card['id']} due_at 无效")
    event_ids = [event["id"] for event in events]
    if len(event_ids) != len(set(event_ids)):
        problems.append("事件 ID 重复")
    checks = {
        "schema_version": state.get("schema_version") == SCHEMA_VERSION,
        "event_log_readable": True,
        "referential_integrity": not problems,
        "integrations": discover_integrations(vault),
        "optional_tools": {
            name: shutil.which(name)
            for name in ("ffmpeg", "yt-dlp", "whisper", "pdftotext", "osascript")
        },
        "optional_python": {
            "pypdf": bool(importlib.util.find_spec("pypdf")),
        },
    }
    emit({"healthy": not problems, "problems": problems, "checks": checks})
    if problems:
        raise KongziError("doctor 检查未通过")


def add_common_vault(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--vault", default=".", help="Obsidian vault 或 Kongzi 工作目录")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kongzi",
        description="Kongzi AI Mentor 的本地状态、证据、复习与报告引擎",
    )
    parser.add_argument("--version", action="version", version="Kongzi 0.1.0")
    sub = parser.add_subparsers(dest="command", required=True)

    init_p = sub.add_parser("init", help="初始化 Obsidian/Kongzi 学习空间")
    add_common_vault(init_p)
    init_p.add_argument("--name", default="")
    init_p.add_argument("--locale", default="zh-CN")
    init_p.add_argument("--timezone", default="Asia/Shanghai")
    init_p.add_argument("--knowledge-base", choices=("new", "existing"), default="existing")
    init_p.add_argument("--goal")
    init_p.add_argument("--outcome")
    init_p.add_argument("--prior-knowledge")
    init_p.add_argument("--deadline")
    init_p.add_argument("--daily-minutes", type=int, default=30)
    init_p.add_argument("--days-per-week", type=int, default=5)
    init_p.add_argument("--constraints")
    init_p.add_argument("--force", action="store_true")
    init_p.set_defaults(func=initialize)

    status_p = sub.add_parser("status", help="显示唯一下一步与完整状态")
    add_common_vault(status_p)
    status_p.set_defaults(func=show_status)

    profile_p = sub.add_parser("profile", help="画像访谈和行为校准")
    profile_sub = profile_p.add_subparsers(dest="profile_command", required=True)
    q_p = profile_sub.add_parser("questionnaire")
    add_common_vault(q_p)
    q_p.set_defaults(func=questionnaire)
    pset = profile_sub.add_parser("set")
    add_common_vault(pset)
    pset.add_argument("--field", required=True)
    pset.add_argument("--value", required=True)
    pset.set_defaults(func=set_profile)
    pobserve = profile_sub.add_parser("observe")
    add_common_vault(pobserve)
    pobserve.add_argument("--dimension", required=True)
    pobserve.add_argument("--observation", required=True)
    pobserve.add_argument("--evidence-id", required=True)
    pobserve.add_argument("--confidence", type=float, default=0.7)
    pobserve.set_defaults(func=observe_profile)

    journey_p = sub.add_parser("journey", help="创建、列出或选择学习旅程")
    journey_sub = journey_p.add_subparsers(dest="journey_command", required=True)
    jcreate = journey_sub.add_parser("create")
    add_common_vault(jcreate)
    jcreate.add_argument("--goal", required=True)
    jcreate.add_argument("--outcome", required=True)
    jcreate.add_argument("--prior-knowledge", default="")
    jcreate.add_argument("--deadline")
    jcreate.add_argument("--daily-minutes", type=int, default=30)
    jcreate.add_argument("--days-per-week", type=int, default=5)
    jcreate.add_argument("--constraints", default="")
    jcreate.set_defaults(func=create_journey)
    jlist = journey_sub.add_parser("list")
    add_common_vault(jlist)
    jlist.set_defaults(func=list_journeys)
    jselect = journey_sub.add_parser("select")
    add_common_vault(jselect)
    jselect.add_argument("journey_id")
    jselect.set_defaults(func=select_journey)

    source_p = sub.add_parser("source", help="录入本地或网页来源")
    source_sub = source_p.add_subparsers(dest="source_command", required=True)
    sadd = source_sub.add_parser("add")
    add_common_vault(sadd)
    sadd.add_argument("path")
    sadd.add_argument("--title")
    sadd.add_argument("--kind")
    sadd.add_argument("--authority", choices=sorted(AUTHORITY_LEVELS), default="user")
    sadd.add_argument("--published-at")
    sadd.add_argument("--author")
    sadd.set_defaults(func=add_source)
    sfetch = source_sub.add_parser("fetch")
    add_common_vault(sfetch)
    sfetch.add_argument("url")
    sfetch.add_argument("--title")
    sfetch.add_argument("--authority", choices=sorted(AUTHORITY_LEVELS), default="official")
    sfetch.add_argument("--published-at")
    sfetch.add_argument("--author")
    sfetch.add_argument("--timeout", type=int, default=30)
    sfetch.add_argument("--max-bytes", type=int, default=10_000_000)
    sfetch.set_defaults(func=fetch_source)
    slist = source_sub.add_parser("list")
    add_common_vault(slist)
    slist.set_defaults(func=list_sources)

    claim_p = sub.add_parser("claim", help="登记带来源定位符的知识主张")
    claim_sub = claim_p.add_subparsers(dest="claim_command", required=True)
    cadd = claim_sub.add_parser("add")
    add_common_vault(cadd)
    cadd.add_argument("--statement", required=True)
    cadd.add_argument("--source-id", required=True)
    cadd.add_argument("--locator", required=True)
    cadd.add_argument("--confidence", type=float, default=0.8)
    cadd.add_argument("--status", choices=("verified", "contested", "unresolved"), default="verified")
    cadd.set_defaults(func=add_claim)

    node_p = sub.add_parser("node", help="构建知识地图节点")
    node_sub = node_p.add_subparsers(dest="node_command", required=True)
    nadd = node_sub.add_parser("add")
    add_common_vault(nadd)
    nadd.add_argument("--title", required=True)
    nadd.add_argument("--knowledge-type", default="concept")
    nadd.add_argument("--prerequisite", action="append", default=[])
    nadd.add_argument("--claim", action="append", default=[])
    nadd.add_argument("--outcome", required=True)
    nadd.add_argument("--difficulty", type=int, choices=range(1, 6), default=2)
    nadd.add_argument("--mastery-threshold", type=float)
    nadd.add_argument("--delayed-passes", type=int)
    nadd.set_defaults(func=add_node)

    map_p = sub.add_parser("map", help="渲染 Mermaid 知识地图")
    map_sub = map_p.add_subparsers(dest="map_command", required=True)
    mrender = map_sub.add_parser("render")
    add_common_vault(mrender)
    mrender.set_defaults(func=render_map)

    plan_p = sub.add_parser("plan", help="按依赖和时间约束制定周期计划")
    plan_sub = plan_p.add_subparsers(dest="plan_command", required=True)
    pbuild = plan_sub.add_parser("build")
    add_common_vault(pbuild)
    pbuild.add_argument("--weeks", type=int, default=4)
    pbuild.add_argument("--sessions-per-week", type=int, default=5)
    pbuild.add_argument("--minutes", type=int, default=30)
    pbuild.add_argument("--start-date")
    pbuild.set_defaults(func=build_plan)

    session_p = sub.add_parser("session", help="执行学习会话的输出—评分—纠错闭环")
    session_sub = session_p.add_subparsers(dest="session_command", required=True)
    sstart = session_sub.add_parser("start")
    add_common_vault(sstart)
    sstart.add_argument("--node-id", required=True)
    sstart.add_argument("--mode", choices=("learn", "practice", "integrate"), default="learn")
    sstart.set_defaults(func=start_session)
    sanswer = session_sub.add_parser("answer")
    add_common_vault(sanswer)
    sanswer.add_argument("--session-id", required=True)
    sanswer.add_argument("--kind", choices=sorted(QUESTION_KINDS), required=True)
    sanswer.add_argument("--question", required=True)
    sanswer.add_argument("--answer", required=True)
    sanswer.set_defaults(func=record_answer)
    sgrade = session_sub.add_parser("grade")
    add_common_vault(sgrade)
    sgrade.add_argument("--answer-id", required=True)
    sgrade.add_argument("--score", type=float, required=True)
    sgrade.add_argument("--feedback", required=True)
    sgrade.add_argument("--correction", required=True)
    sgrade.add_argument("--claim", action="append", default=[])
    sgrade.add_argument("--retrieval", type=float, default=0.0)
    sgrade.add_argument("--accuracy", type=float, default=0.0)
    sgrade.add_argument("--transfer", type=float, default=0.0)
    sgrade.set_defaults(func=grade_answer)
    sfinish = session_sub.add_parser("finish")
    add_common_vault(sfinish)
    sfinish.add_argument("--session-id", required=True)
    sfinish.add_argument("--minutes", type=int, required=True)
    sfinish.add_argument("--reflection", required=True)
    sfinish.add_argument("--confidence", type=float, required=True)
    sfinish.set_defaults(func=finish_session)

    review_p = sub.add_parser("review", help="到期复习与间隔调度")
    review_sub = review_p.add_subparsers(dest="review_command", required=True)
    rdue = review_sub.add_parser("due")
    add_common_vault(rdue)
    rdue.add_argument("--all-journeys", action="store_true")
    rdue.set_defaults(func=show_due)
    ranswer = review_sub.add_parser("answer")
    add_common_vault(ranswer)
    ranswer.add_argument("--card-id", required=True)
    ranswer.add_argument("--answer", required=True)
    ranswer.add_argument("--score", type=float, required=True)
    ranswer.add_argument("--feedback", required=True)
    ranswer.add_argument("--allow-early", action="store_true")
    ranswer.set_defaults(func=review_answer)
    rsnooze = review_sub.add_parser("snooze")
    add_common_vault(rsnooze)
    rsnooze.add_argument("--card-id", required=True)
    rsnooze.add_argument("--hours", type=int, default=24)
    rsnooze.set_defaults(func=snooze_review)

    note_p = sub.add_parser("note", help="写入 Obsidian 学习笔记")
    note_sub = note_p.add_subparsers(dest="note_command", required=True)
    ncapture = note_sub.add_parser("capture")
    add_common_vault(ncapture)
    ncapture.add_argument("--title", required=True)
    ncapture.add_argument("--body", required=True)
    ncapture.add_argument("--claim", action="append", default=[])
    ncapture.set_defaults(func=capture_note)

    report_p = sub.add_parser("report", help="生成可追溯日报或周报")
    report_sub = report_p.add_subparsers(dest="report_command", required=True)
    for kind in ("daily", "weekly"):
        rp = report_sub.add_parser(kind)
        add_common_vault(rp)
        rp.add_argument("--date")
        rp.set_defaults(func=generate_report, kind=kind)
    rauto = report_sub.add_parser("auto")
    add_common_vault(rauto)
    rauto.set_defaults(func=generate_auto_reports)

    mentor_p = sub.add_parser("mentor", help="启用/停用 Nuwa 导师人格")
    mentor_sub = mentor_p.add_subparsers(dest="mentor_command", required=True)
    mset = mentor_sub.add_parser("set")
    add_common_vault(mset)
    mset.add_argument("--name", required=True)
    mset.add_argument("--persona-path", required=True)
    mset.set_defaults(func=set_mentor)
    moff = mentor_sub.add_parser("off")
    add_common_vault(moff)
    moff.set_defaults(func=disable_mentor)

    integration_p = sub.add_parser("integration", help="Cangjie/Nuwa/Darwin/video-downloader 桥接")
    integration_sub = integration_p.add_subparsers(dest="integration_command", required=True)
    istatus = integration_sub.add_parser("status")
    add_common_vault(istatus)
    istatus.set_defaults(func=integration_status)
    iprepare = integration_sub.add_parser("prepare")
    add_common_vault(iprepare)
    iprepare.add_argument("integration", choices=tuple(INTEGRATION_NAMES))
    iprepare.set_defaults(func=prepare_integration)
    icangjie = integration_sub.add_parser("import-cangjie")
    add_common_vault(icangjie)
    icangjie.add_argument("--output-dir", required=True)
    icangjie.set_defaults(func=import_cangjie)
    inuw = integration_sub.add_parser("import-nuwa")
    add_common_vault(inuw)
    inuw.add_argument("--name", required=True)
    inuw.add_argument("--persona-path", required=True)
    inuw.set_defaults(func=import_nuwa)
    ivideo = integration_sub.add_parser("run-video")
    add_common_vault(ivideo)
    ivideo.add_argument("url")
    ivideo.add_argument("--output-dir", required=True)
    ivideo.add_argument("--title")
    ivideo.add_argument("--authority", choices=sorted(AUTHORITY_LEVELS), default="user")
    ivideo.add_argument("--asr-backend", choices=("auto", "siliconflow", "whisper", "none"))
    ivideo.add_argument("--asr-model")
    ivideo.add_argument("--asr-language")
    ivideo.add_argument("--asr-max-seconds", type=float)
    ivideo.add_argument("--metadata-only", action="store_true")
    ivideo.set_defaults(func=run_video)

    reminder_p = sub.add_parser("reminder", help="生成、安装或触发系统复习提醒")
    reminder_sub = reminder_p.add_subparsers(dest="reminder_command", required=True)
    rgenerate = reminder_sub.add_parser("generate")
    add_common_vault(rgenerate)
    rgenerate.add_argument("--method", choices=("launchd", "cron"), default="launchd")
    rgenerate.add_argument("--time", default="20:00")
    rgenerate.set_defaults(func=reminder_generate)
    rinstall = reminder_sub.add_parser("install")
    add_common_vault(rinstall)
    rinstall.set_defaults(func=reminder_install)
    rnotify = reminder_sub.add_parser("notify")
    add_common_vault(rnotify)
    rnotify.add_argument("--reports", action="store_true")
    rnotify.set_defaults(func=reminder_notify)

    doctor_p = sub.add_parser("doctor", help="检查状态、证据与工具完整性")
    add_common_vault(doctor_p)
    doctor_p.set_defaults(func=doctor)
    repair_p = sub.add_parser("repair", help="从追加事件日志重建损坏的状态索引")
    add_common_vault(repair_p)
    repair_p.add_argument(
        "--component",
        choices=("all", "state", "profile", "queue"),
        default="all",
    )
    repair_p.set_defaults(func=repair)
    bundle_p = sub.add_parser("bundle", help="导出或导入可校验的跨 runtime 学习包")
    bundle_sub = bundle_p.add_subparsers(dest="bundle_command", required=True)
    bexport = bundle_sub.add_parser("export")
    add_common_vault(bexport)
    bexport.add_argument("--output", required=True)
    bexport.add_argument("--overwrite", action="store_true")
    bexport.set_defaults(func=export_bundle)
    bimport = bundle_sub.add_parser("import")
    add_common_vault(bimport)
    bimport.add_argument("--bundle", required=True)
    bimport.set_defaults(func=import_bundle)
    migrate_p = sub.add_parser("migrate", help="检查并迁移 Kongzi 状态 schema")
    add_common_vault(migrate_p)
    migrate_p.set_defaults(func=migrate)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except KongziError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print(json.dumps({"ok": False, "error": "用户中断"}, ensure_ascii=False), file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
