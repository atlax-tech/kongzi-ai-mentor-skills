#!/usr/bin/env python3
"""Render assets/demo.gif from a real temporary Kongzi CLI learning cycle."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover - developer-only asset tool
    raise SystemExit("Demo rendering needs Pillow: python3 -m pip install Pillow") from exc


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "kongzi.py"
WIDTH, HEIGHT = 1280, 720
BG = "#0b1220"
PANEL = "#111c2f"
INK = "#e6edf7"
MUTED = "#8fa5c3"
JADE = "#5ee0bd"
GOLD = "#f1c779"
BLUE = "#79a9ff"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("/System/Library/Fonts/SFNSMono.ttf"),
        Path("/System/Library/Fonts/Menlo.ttc"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
    ]
    if bold:
        candidates.insert(0, Path("/System/Library/Fonts/SFNSMonoBold.ttf"))
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


TITLE_FONT = font(30, bold=True)
BODY_FONT = font(24)
SMALL_FONT = font(19)


def command(*args: str) -> dict:
    completed = subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    if completed.returncode:
        raise RuntimeError(f"{completed.args}\n{completed.stderr}")
    return json.loads(completed.stdout)


def render_frame(step: int, title: str, typed: str, lines: list[tuple[str, str]]) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((42, 38, WIDTH - 42, HEIGHT - 38), radius=22, fill=PANEL)
    for index, color in enumerate(("#ff6b6b", "#f5c451", "#55cf89")):
        x = 74 + index * 28
        draw.ellipse((x, 68, x + 14, 82), fill=color)
    draw.text((WIDTH - 232, 59), f"KONGZI  {step:02d}", font=SMALL_FONT, fill=MUTED)
    draw.text((76, 118), title, font=TITLE_FONT, fill=INK)
    draw.rounded_rectangle((70, 174, WIDTH - 70, 240), radius=10, fill="#08101d")
    draw.text((92, 190), f"$ {typed}", font=BODY_FONT, fill=JADE)
    y = 282
    for text, color in lines:
        wrapped = textwrap.wrap(text, width=78) or [""]
        for part in wrapped:
            draw.text((92, y), part, font=BODY_FONT, fill=color)
            y += 39
        y += 8
    draw.text(
        (76, HEIGHT - 78),
        "source -> map -> output -> feedback -> spaced review",
        font=SMALL_FONT,
        fill=MUTED,
    )
    return image


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ROOT / "assets" / "demo.gif"))
    args = parser.parse_args()
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="kongzi-demo-") as raw_temp:
        vault = Path(raw_temp) / "ObsidianVault"
        init = command(
            "init",
            "--vault",
            str(vault),
            "--name",
            "Ada",
            "--goal",
            "Learn retrieval practice",
            "--outcome",
            "Design a one-week study protocol",
        )
        frames = [
            render_frame(
                1,
                "Start a personalized learning journey",
                "/Kongzi",
                [
                    ("vault: initialized as an Obsidian-compatible workspace", BLUE),
                    (f"journey: {init['journey']['journey']['goal']}", INK),
                    ("next: one-question-at-a-time learner diagnosis", GOLD),
                ],
            )
        ]
        for field, value in (
            ("goal", "Build a usable study protocol"),
            ("baseline", "I mostly reread notes"),
            ("constraints", "30 minutes each weekday"),
            ("materials", "research papers and my notes"),
            ("experience", "I forget after a few days"),
            ("diagnostic", "retrieval means recalling without the answer"),
        ):
            command(
                "profile",
                "set",
                "--vault",
                str(vault),
                "--field",
                field,
                "--value",
                value,
            )
        frames.append(
            render_frame(
                2,
                "Build a calibrated learner profile",
                "/Kongzi profile",
                [
                    ("self-report: stored separately from observed performance", INK),
                    ("constraint: 30 minutes / weekday", BLUE),
                    ("diagnostic: future answers will calibrate the profile", GOLD),
                ],
            )
        )
        source_file = Path(raw_temp) / "retrieval-practice.md"
        source_file.write_text(
            "# Retrieval practice\n\nDelayed retrieval supports durable access when feedback corrects errors.\n",
            encoding="utf-8",
        )
        source = command(
            "source",
            "add",
            "--vault",
            str(vault),
            str(source_file),
            "--authority",
            "primary",
            "--title",
            "Retrieval practice paper",
        )["source"]
        claim = command(
            "claim",
            "add",
            "--vault",
            str(vault),
            "--statement",
            "Delayed retrieval with corrective feedback supports durable access.",
            "--source-id",
            source["id"],
            "--locator",
            "Retrieval practice, paragraph 1",
        )["claim"]
        frames.append(
            render_frame(
                3,
                "Ground teaching in inspectable evidence",
                "/Kongzi source add retrieval-practice.md",
                [
                    (f"source_id: {source['id']}", BLUE),
                    (f"sha256: {source['sha256'][:24]}...", MUTED),
                    (f"claim locator: {claim['locator']}", GOLD),
                ],
            )
        )
        node = command(
            "node",
            "add",
            "--vault",
            str(vault),
            "--title",
            "Retrieval practice",
            "--knowledge-type",
            "procedure",
            "--claim",
            claim["id"],
            "--outcome",
            "Create three retrieval prompts",
        )["node"]
        map_result = command("map", "render", "--vault", str(vault))
        plan = command(
            "plan",
            "build",
            "--vault",
            str(vault),
            "--weeks",
            "1",
            "--sessions-per-week",
            "3",
            "--minutes",
            "25",
        )["plan"]
        frames.append(
            render_frame(
                4,
                "Create a prerequisite-aware map and cycle",
                "/Kongzi roadmap",
                [
                    (f"knowledge map: {map_result['nodes']} grounded node", BLUE),
                    (f"cycle: {len(plan['sessions'])} sessions x 25 minutes", INK),
                    ("method fit: procedure -> example, attempt, feedback, transfer", GOLD),
                ],
            )
        )
        session = command(
            "session", "start", "--vault", str(vault), "--node-id", node["id"]
        )["session"]
        frames.append(
            render_frame(
                5,
                "The mentor asks — the learner must output",
                "/Kongzi study",
                [
                    ("Question: How would you learn tree traversal durably?", INK),
                    ("> Recall it on a blank page, check errors, retry tomorrow.", JADE),
                    ("Kongzi records the answer verbatim before feedback.", MUTED),
                ],
            )
        )
        answer = command(
            "session",
            "answer",
            "--vault",
            str(vault),
            "--session-id",
            session["id"],
            "--kind",
            "application",
            "--question",
            "How would you learn tree traversal durably?",
            "--answer",
            "Recall it on a blank page, check errors, retry tomorrow.",
        )["answer"]
        graded = command(
            "session",
            "grade",
            "--vault",
            str(vault),
            "--answer-id",
            answer["id"],
            "--score",
            "0.86",
            "--feedback",
            "Good retrieval and delay.",
            "--correction",
            "Add a novel traversal problem for transfer.",
            "--claim",
            claim["id"],
            "--retrieval",
            "0.9",
            "--accuracy",
            "0.9",
            "--transfer",
            "0.78",
        )
        command(
            "session",
            "finish",
            "--vault",
            str(vault),
            "--session-id",
            session["id"],
            "--minutes",
            "25",
            "--reflection",
            "Output before rereading.",
            "--confidence",
            "0.72",
        )
        frames.append(
            render_frame(
                6,
                "Feedback becomes future review evidence",
                "/Kongzi grade",
                [
                    ("score: 0.86  |  retrieval 0.90  |  transfer 0.78", BLUE),
                    ("correction: add a novel problem for transfer", GOLD),
                    (f"review due: {graded['review_card']['due_at'][:10]}", JADE),
                ],
            )
        )
        report = command("report", "daily", "--vault", str(vault))["report"]
        status = command("status", "--vault", str(vault))
        frames.append(
            render_frame(
                7,
                "Resume from durable progress — not chat memory",
                "/Kongzi",
                [
                    (f"finished sessions: {report['sessions_finished']}", INK),
                    (f"average score: {report['average_score']}", BLUE),
                    (f"one next move: {status['next_action']}", GOLD),
                ],
            )
        )

    expanded: list[Image.Image] = []
    for frame in frames:
        expanded.extend([frame] * 5)
    expanded[0].save(
        output,
        save_all=True,
        append_images=expanded[1:],
        duration=220,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(json.dumps({"output": str(output), "frames": len(frames)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
