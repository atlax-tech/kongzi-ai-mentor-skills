#!/usr/bin/env python3
"""Render a narrative Kongzi product demo from a real temporary learning journey."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover - developer-only asset tool
    raise SystemExit("Demo rendering needs Pillow: python3 -m pip install Pillow") from exc


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "kongzi.py"
WIDTH, HEIGHT = 960, 540

BG = "#070d17"
SHELL = "#0c1524"
PANEL = "#111d2e"
PANEL_2 = "#162438"
INK = "#eef3ed"
MUTED = "#91a39f"
FAINT = "#526761"
JADE = "#70e1be"
GOLD = "#efc66f"
BLUE = "#78a7ff"
RED = "#ff8a7a"


def font(
    size: int, *, bold: bool = False, mono: bool = False
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if mono:
        candidates = [
            Path("/System/Library/Fonts/Menlo.ttc"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
        ]
    else:
        candidates = [
            Path("/System/Library/Fonts/PingFang.ttc"),
            Path("/System/Library/Fonts/STHeiti Medium.ttc"),
            Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ]
    for path in candidates:
        if path.exists():
            try:
                return ImageFont.truetype(
                    str(path),
                    size=size,
                    index=4 if bold and path.suffix == ".ttc" and not mono else 0,
                )
            except OSError:
                return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


F_HERO = font(38, bold=True)
F_H1 = font(25, bold=True)
F_H2 = font(18, bold=True)
F_BODY = font(15)
F_SMALL = font(12)
F_TINY = font(10)
F_MONO = font(14, mono=True)
F_MONO_SMALL = font(11, mono=True)


def command(*args: str) -> dict[str, Any]:
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


def ease(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3 - 2 * value)


def reveal(t: float, start: float, end: float) -> float:
    return ease((t - start) / max(0.001, end - start))


def mix(a: float, b: float, amount: float) -> float:
    return a + (b - a) * ease(amount)


def layer() -> Image.Image:
    return Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))


def text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    value: str,
    used_font: ImageFont.ImageFont,
    fill: str | tuple[int, int, int, int] = INK,
    *,
    anchor: str | None = None,
) -> None:
    draw.text(xy, value, font=used_font, fill=fill, anchor=anchor)


def pill(
    draw: ImageDraw.ImageDraw,
    box: tuple[float, float, float, float],
    value: str,
    *,
    fill: str = PANEL_2,
    outline: str = FAINT,
    color: str = INK,
) -> None:
    draw.rounded_rectangle(box, radius=9, fill=fill, outline=outline, width=1)
    x1, y1, x2, y2 = box
    text(draw, ((x1 + x2) / 2, (y1 + y2) / 2), value, F_TINY, color, anchor="mm")


def shell(step: int, title: str, subtitle: str) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((18, 16, WIDTH - 18, HEIGHT - 16), radius=18, fill=SHELL, outline="#203149")
    draw.line((18, 66, WIDTH - 18, 66), fill="#203149", width=1)
    text(draw, (38, 35), "KONGZI", F_H2, GOLD)
    text(draw, (116, 37), "AI LEARNING MENTOR", F_TINY, MUTED)
    text(draw, (WIDTH - 38, 37), "SQL 业务分析 · 4 周", F_SMALL, MUTED, anchor="ra")
    text(draw, (40, 91), f"0{step}", F_SMALL, JADE)
    text(draw, (74, 86), title, F_H1, INK)
    text(draw, (74, 119), subtitle, F_SMALL, MUTED)
    return image


def footer(draw: ImageDraw.ImageDraw, active: int) -> None:
    labels = ("画像", "资料", "路线", "学习", "复习")
    left, right, y = 54, WIDTH - 54, HEIGHT - 40
    gap = (right - left) / (len(labels) - 1)
    draw.line((left, y - 9, right, y - 9), fill="#26384a", width=2)
    if active:
        draw.line((left, y - 9, left + gap * (active - 1), y - 9), fill=JADE, width=3)
    for index, label_value in enumerate(labels):
        x = left + gap * index
        color = GOLD if index + 1 == active else JADE if index + 1 < active else FAINT
        draw.ellipse((x - 4, y - 13, x + 4, y - 5), fill=color)
        text(draw, (x, y + 2), label_value, F_TINY, color, anchor="ma")


def card(
    draw: ImageDraw.ImageDraw,
    box: tuple[float, float, float, float],
    *,
    fill: str = PANEL,
    outline: str = "#26384a",
    radius: int = 14,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=1)


def metric(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    label_value: str,
    value: str,
    color: str,
) -> None:
    text(draw, (x, y), label_value, F_TINY, MUTED)
    text(draw, (x, y + 20), value, F_H2, color)


def scene_intro(t: float, data: dict[str, Any]) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    grid_alpha = int(34 * reveal(t, 0.0, 0.45))
    for x in range(0, WIDTH, 48):
        draw.line((x, 0, x, HEIGHT), fill=(28, 48, 66, grid_alpha), width=1)
    for y in range(0, HEIGHT, 48):
        draw.line((0, y, WIDTH, y), fill=(28, 48, 66, grid_alpha), width=1)
    a = reveal(t, 0.05, 0.30)
    text(draw, (WIDTH / 2, 122), "KONGZI · 孔子", F_SMALL, GOLD, anchor="mm")
    text(draw, (WIDTH / 2, 190), "不是再给你一张课表", F_HERO, INK, anchor="mm")
    crossed = reveal(t, 0.30, 0.48)
    line_width = int(440 * crossed)
    draw.line(
        (WIDTH / 2 - line_width / 2, 194, WIDTH / 2 + line_width / 2, 194),
        fill=RED,
        width=3,
    )
    b = reveal(t, 0.42, 0.70)
    text(draw, (WIDTH / 2, 264), "而是陪你把知识学会、记住、用出来", F_H1, JADE, anchor="mm")
    box_width = mix(0, 650, b)
    card(draw, (WIDTH / 2 - box_width / 2, 325, WIDTH / 2 + box_width / 2, 399))
    if b > 0.72:
        text(draw, (WIDTH / 2, 349), "目标：4 周后独立完成一次 SQL 业务分析", F_H2, INK, anchor="mm")
        text(draw, (WIDTH / 2, 379), "每天 30 分钟 · 零基础 · 用自己的资料学习", F_SMALL, MUTED, anchor="mm")
    c = reveal(t, 0.72, 0.94)
    text(draw, (WIDTH / 2, 458), "下面是一条由真实状态引擎生成的完整链路", F_SMALL, (145, 163, 159, int(255 * c)), anchor="mm")
    return image


def scene_profile(t: float, data: dict[str, Any]) -> Image.Image:
    image = shell(1, "先认识你，不先给你课程表", "画像来自自述 + 闭卷诊断，后续会被真实表现持续校准")
    draw = ImageDraw.Draw(image)
    shift = int(28 * (1 - reveal(t, 0.02, 0.24)))
    card(draw, (42 - shift, 152, 538 - shift, 418))
    text(draw, (66 - shift, 175), "Kongzi", F_SMALL, JADE)
    text(draw, (66 - shift, 205), "4 周后，你要独立完成什么？", F_H2, INK)
    card(draw, (92 - shift, 248, 514 - shift, 326), fill=PANEL_2)
    text(draw, (112 - shift, 268), "我想拿一份订单数据，自己写查询、", F_BODY, INK)
    text(draw, (112 - shift, 293), "解释结果，并找出一个业务问题。", F_BODY, INK)
    text(draw, (66 - shift, 355), "闭卷诊断", F_TINY, MUTED)
    text(draw, (150 - shift, 352), "SELECT 会一点；GROUP BY 不会", F_SMALL, GOLD)

    right_x = int(mix(990, 570, reveal(t, 0.18, 0.50)))
    card(draw, (right_x, 152, right_x + 346, 418))
    text(draw, (right_x + 22, 174), "学习者画像", F_H2, INK)
    items = (
        ("目标", "业务数据分析"),
        ("基础", "零基础 / 有少量 SELECT"),
        ("节奏", "30 分钟 × 每周 5 天"),
        ("材料", "官方文档 + 自己的数据"),
        ("阻力", "看懂后很快忘"),
    )
    for index, (key, value) in enumerate(items):
        row_alpha = reveal(t, 0.35 + index * 0.08, 0.50 + index * 0.08)
        y = 215 + index * 37
        text(draw, (right_x + 22, y), key, F_TINY, MUTED)
        if row_alpha > 0.4:
            text(draw, (right_x + 88, y - 2), value, F_SMALL, INK)
            draw.line((right_x + 22, y + 25, right_x + 322, y + 25), fill="#26384a")
    footer(draw, 1)
    return image


def scene_sources(t: float, data: dict[str, Any]) -> Image.Image:
    image = shell(2, "知识先有出处，再进入路线", "资料、定位符和哈希被保存；知识地图只接受有来源的主张")
    draw = ImageDraw.Draw(image)
    sources = (
        ("OFFICIAL", "PostgreSQL SELECT 文档", "section: GROUP BY"),
        ("USER", "orders.csv + 业务说明", "本地材料"),
        ("PRIMARY", "SQL 标准摘录", "7.9 grouped table"),
    )
    for index, (badge, title_value, locator) in enumerate(sources):
        x = int(mix(-260, 44, reveal(t, 0.03 + index * 0.08, 0.28 + index * 0.08)))
        y = 162 + index * 78
        card(draw, (x, y, x + 280, y + 62))
        pill(draw, (x + 14, y + 12, x + 80, y + 33), badge, color=JADE)
        text(draw, (x + 94, y + 11), title_value, F_SMALL, INK)
        text(draw, (x + 94, y + 35), locator, F_TINY, MUTED)

    prism_x = 424
    glow = reveal(t, 0.35, 0.60)
    draw.polygon(
        ((prism_x, 220), (prism_x + 52, 252), (prism_x, 284), (prism_x - 52, 252)),
        fill="#183d3c",
        outline=JADE,
    )
    text(draw, (prism_x, 250), "3", F_H1, GOLD, anchor="mm")
    text(draw, (prism_x, 307), "VERIFIED CLAIMS", F_TINY, JADE, anchor="mm")
    for index in range(3):
        start_y = 193 + index * 78
        amount = reveal(t, 0.25 + index * 0.07, 0.52 + index * 0.07)
        draw.line((324, start_y, mix(324, prism_x - 55, amount), 252), fill=JADE, width=2)

    nodes = (
        (610, 175, "SELECT / WHERE", BLUE),
        (758, 247, "GROUP BY", GOLD),
        (610, 331, "窗口函数", JADE),
    )
    for index, (x, y, label_value, color) in enumerate(nodes):
        amount = reveal(t, 0.52 + index * 0.06, 0.72 + index * 0.06)
        radius = int(34 * amount)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=PANEL_2, outline=color, width=2)
        if amount > 0.65:
            text(draw, (x, y), label_value, F_TINY, color, anchor="mm")
    graph_amount = reveal(t, 0.62, 0.86)
    draw.line((644, 190, mix(644, 724, graph_amount), mix(190, 239, graph_amount)), fill=FAINT, width=2)
    draw.line((728, 268, mix(728, 644, graph_amount), mix(268, 320, graph_amount)), fill=FAINT, width=2)
    text(draw, (754, 373), "依赖关系，不是平铺目录", F_SMALL, MUTED, anchor="mm")
    footer(draw, 2)
    return image


def scene_roadmap(t: float, data: dict[str, Any]) -> Image.Image:
    image = shell(3, "路线按你的时间与能力定制", "每次学习都有可检查产出；忙碌日也有最小可行任务")
    draw = ImageDraw.Draw(image)
    card(draw, (42, 153, 918, 352))
    weeks = (
        ("W1", "查询基础", "写出 5 个可运行查询"),
        ("W2", "分组聚合", "解释 GROUP BY 边界"),
        ("W3", "连接与窗口", "调试一份错误查询"),
        ("W4", "业务项目", "提交分析 + 口头复盘"),
    )
    for index, (week, title_value, output) in enumerate(weeks):
        x = 66 + index * 211
        amount = reveal(t, 0.06 + index * 0.10, 0.30 + index * 0.10)
        draw.line((x + 36, 205, x + 36, 318), fill=JADE if index < 2 else FAINT, width=3)
        draw.ellipse((x + 29, 191, x + 43, 205), fill=GOLD if index == 1 else JADE if index == 0 else FAINT)
        if amount > 0.35:
            text(draw, (x, 171), week, F_TINY, GOLD if index == 1 else MUTED)
            text(draw, (x, 222), title_value, F_H2, INK)
            text(draw, (x, 255), "5 × 30min", F_SMALL, BLUE)
            text(draw, (x, 286), output, F_TINY, MUTED)
    arrow_amount = reveal(t, 0.52, 0.76)
    draw.line((102, 198, mix(102, 735, arrow_amount), 198), fill=GOLD, width=2)

    card(draw, (42, 370, 600, 448), fill=PANEL_2)
    text(draw, (62, 387), "本周方法匹配", F_TINY, MUTED)
    text(draw, (62, 414), "示例 → 自己写 → 纠错 → 变式迁移", F_H2, JADE)
    pill(draw, (642, 381, 745, 415), "正常日 · 30min", color=INK)
    pill(draw, (760, 381, 895, 415), "忙碌日 · 8min", color=GOLD)
    footer(draw, 3)
    return image


def bar(draw: ImageDraw.ImageDraw, y: int, label_value: str, value: float, color: str, t: float) -> None:
    text(draw, (610, y), label_value, F_TINY, MUTED)
    draw.rounded_rectangle((684, y + 2, 866, y + 12), radius=5, fill="#233247")
    width = 182 * value * reveal(t, 0.45, 0.80)
    draw.rounded_rectangle((684, y + 2, 684 + width, y + 12), radius=5, fill=color)
    if t > 0.68:
        text(draw, (884, y), f"{value:.2f}", F_TINY, color, anchor="ra")


def scene_study(t: float, data: dict[str, Any]) -> Image.Image:
    image = shell(4, "老师先提问，等你真正输出", "原始作答先保存，再按提取、准确与迁移分别反馈")
    draw = ImageDraw.Draw(image)
    card(draw, (42, 151, 572, 236))
    text(draw, (62, 171), "闭卷题", F_TINY, GOLD)
    text(draw, (62, 198), "求每个客户的订单总额。请写 SQL，并解释为什么要分组。", F_BODY, INK)
    card(draw, (42, 252, 572, 425), fill="#0a111c")
    typed = (
        "SELECT customer_id, SUM(amount)\n"
        "FROM orders\n"
        "GROUP BY customer_id;"
    )
    chars = int(len(typed) * reveal(t, 0.12, 0.57))
    y = 278
    for line_value in typed[:chars].splitlines():
        text(draw, (66, y), line_value, F_MONO, JADE)
        y += 31
    if t > 0.58:
        text(draw, (66, 389), "因为要按客户分别聚合。", F_SMALL, INK)

    panel_x = int(mix(980, 594, reveal(t, 0.48, 0.72)))
    card(draw, (panel_x, 151, panel_x + 324, 425))
    text(draw, (panel_x + 20, 173), "已记录原始作答", F_SMALL, JADE)
    text(draw, (panel_x + 20, 205), "不是“看起来懂了”", F_H2, INK)
    bar(draw, 252, "提取", 0.90, BLUE, t)
    bar(draw, 294, "准确", 0.92, JADE, t)
    bar(draw, 336, "迁移", 0.78, GOLD, t)
    if t > 0.78:
        text(draw, (panel_x + 20, 380), "下一步：换一个维度再次分组", F_SMALL, GOLD)
    footer(draw, 4)
    return image


def chat_bubble(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    who: str,
    lines: tuple[str, ...],
    *,
    accent: str,
    fill: str = PANEL,
) -> None:
    card(draw, box, fill=fill)
    x1, y1, _, _ = box
    text(draw, (x1 + 18, y1 + 14), who, F_TINY, accent)
    for index, line_value in enumerate(lines):
        text(draw, (x1 + 18, y1 + 38 + index * 23), line_value, F_SMALL, INK)


def scene_question(t: float, data: dict[str, Any]) -> Image.Image:
    image = shell(4, "你可以随时打断，导师必须耐心回答", "问题会被保存；讲解必须有来源，随后必须让你复述")
    draw = ImageDraw.Draw(image)
    y1 = int(mix(520, 155, reveal(t, 0.02, 0.24)))
    chat_bubble(
        draw,
        (42, y1, 562, y1 + 72),
        "你",
        ("为什么 customer_id 必须出现在 GROUP BY？",),
        accent=GOLD,
        fill=PANEL_2,
    )
    y2 = int(mix(540, 240, reveal(t, 0.22, 0.50)))
    chat_bubble(
        draw,
        (88, y2, 680, y2 + 112),
        "Kongzi · 有据讲解",
        (
            "分组后，每组必须对应一个确定的 customer_id；",
            "否则数据库无法决定这一行该显示哪个客户。",
            f"证据：{data['claim_short']} · PostgreSQL / GROUP BY",
        ),
        accent=JADE,
    )
    y3 = int(mix(560, 368, reveal(t, 0.48, 0.72)))
    chat_bubble(
        draw,
        (212, y3, 790, y3 + 70),
        "Kongzi · 理解检查",
        ("如果还要按月份聚合，你会改哪两处？先用自己的话回答。",),
        accent=BLUE,
        fill="#12223a",
    )
    if t > 0.76:
        pill(draw, (810, 379, 902, 415), "等待你输出…", color=GOLD)
    footer(draw, 4)
    return image


def scene_review(t: float, data: dict[str, Any]) -> Image.Image:
    image = shell(5, "反馈自动进入复习与进度证据", "即时高分不等于掌握；系统会在延迟后重新提取并检查迁移")
    draw = ImageDraw.Draw(image)
    card(draw, (42, 150, 516, 426))
    text(draw, (66, 173), "间隔复习队列", F_H2, INK)
    points = ((94, "今天"), (184, "+1天"), (284, "+3天"), (394, "+7天"))
    progress = reveal(t, 0.08, 0.70)
    draw.line((94, 246, mix(94, 394, progress), 246), fill=JADE, width=3)
    for index, (x, label_value) in enumerate(points):
        active = progress >= index / (len(points) - 1)
        draw.ellipse((x - 8, 238, x + 8, 254), fill=GOLD if index == 1 else JADE if active else FAINT)
        text(draw, (x, 271), label_value, F_TINY, GOLD if index == 1 else MUTED, anchor="ma")
    card(draw, (66, 309, 488, 394), fill=PANEL_2)
    text(draw, (86, 328), "GROUP BY 变式题", F_SMALL, INK)
    text(draw, (86, 355), "到期：明天 20:00 · 不显示原答案", F_TINY, MUTED)
    pill(draw, (367, 327, 466, 361), "已安排提醒", color=JADE)

    right_x = int(mix(980, 542, reveal(t, 0.38, 0.65)))
    card(draw, (right_x, 150, right_x + 376, 426))
    text(draw, (right_x + 22, 173), "今日学习证据", F_H2, INK)
    metric(draw, right_x + 22, 215, "学习时长", f"{data['minutes']} min", BLUE)
    metric(draw, right_x + 145, 215, "已评分输出", str(data["graded"]), JADE)
    metric(draw, right_x + 270, 215, "已回答疑问", str(data["questions"]), GOLD)
    draw.line((right_x + 22, 282, right_x + 354, 282), fill="#26384a")
    text(draw, (right_x + 22, 307), "当前状态", F_TINY, MUTED)
    text(draw, (right_x + 22, 332), "Level 2 · Reviewing", F_H2, GOLD)
    text(draw, (right_x + 22, 364), "尚未掌握：还需 2 次延迟成功 + 迁移任务", F_SMALL, INK)
    text(draw, (right_x + 22, 395), "唯一下一步：明天完成到期复习", F_SMALL, JADE)
    footer(draw, 5)
    return image


def scene_outro(t: float, data: dict[str, Any]) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    text(draw, (WIDTH / 2, 66), "一次完整学习后，留下的不是聊天记录", F_H1, INK, anchor="mm")
    text(draw, (WIDTH / 2, 104), "而是一套能继续教你的个人学习系统", F_H2, JADE, anchor="mm")
    items = (
        ("画像", "目标、基础、时间与阻力"),
        ("来源", "资料、哈希、定位符与主张"),
        ("地图", "知识节点、依赖与掌握标准"),
        ("课堂", "原始作答、疑问、讲解与纠错"),
        ("复习", "到期队列、提醒与延迟证据"),
        ("报告", "日报、周报与唯一下一步"),
    )
    for index, (title_value, subtitle) in enumerate(items):
        row, col = divmod(index, 3)
        amount = reveal(t, 0.05 + index * 0.07, 0.25 + index * 0.07)
        x = int(mix(-260 if col == 0 else WIDTH + 80, 55 + col * 294, amount))
        y = 154 + row * 112
        card(draw, (x, y, x + 262, y + 86), fill=PANEL)
        text(draw, (x + 18, y + 16), title_value, F_H2, GOLD if index in (0, 3) else JADE)
        text(draw, (x + 18, y + 49), subtitle, F_SMALL, MUTED)
    line_amount = reveal(t, 0.68, 0.92)
    draw.line((180, 411, mix(180, 780, line_amount), 411), fill=GOLD, width=2)
    if t > 0.74:
        text(draw, (WIDTH / 2, 455), "有据地学 · 主动地答 · 耐心地教 · 按时地习", F_H2, INK, anchor="mm")
        text(draw, (WIDTH / 2, 495), "/Kongzi  从你的下一项能力开始", F_SMALL, GOLD, anchor="mm")
    return image


def build_demo_data() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="kongzi-demo-") as raw_temp:
        vault = Path(raw_temp) / "ObsidianVault"
        command(
            "init",
            "--vault",
            str(vault),
            "--name",
            "Ada",
            "--goal",
            "4 周内学会 SQL 业务分析",
            "--outcome",
            "独立完成订单数据分析并解释查询结果",
            "--daily-minutes",
            "30",
            "--days-per-week",
            "5",
        )
        for field, value in (
            ("goal", "独立完成 SQL 业务分析"),
            ("baseline", "会少量 SELECT，不会 GROUP BY"),
            ("constraints", "每天 30 分钟，每周 5 天"),
            ("materials", "官方文档和自己的订单数据"),
            ("experience", "看懂后几天就忘"),
            ("diagnostic", "能筛选行，不能解释分组聚合"),
        ):
            command("profile", "set", "--vault", str(vault), "--field", field, "--value", value)

        source_file = Path(raw_temp) / "postgresql-select.md"
        source_file.write_text(
            "# PostgreSQL SELECT — GROUP BY excerpt\n\n"
            "GROUP BY condenses rows that share the same values for the grouped expressions "
            "into a single group row. Aggregate functions compute a single result from each group.\n",
            encoding="utf-8",
        )
        source = command(
            "source",
            "add",
            "--vault",
            str(vault),
            str(source_file),
            "--authority",
            "official",
            "--title",
            "PostgreSQL SELECT documentation",
        )["source"]
        claims = []
        for statement, locator in (
            (
                "GROUP BY condenses rows sharing values in grouping expressions into one group row.",
                "GROUP BY excerpt, sentence 1",
            ),
            (
                "Aggregate functions compute one result from each group.",
                "GROUP BY excerpt, sentence 2",
            ),
            (
                "A selected non-aggregate expression must identify a value for each group.",
                "GROUP BY excerpt, derived boundary",
            ),
        ):
            claims.append(
                command(
                    "claim",
                    "add",
                    "--vault",
                    str(vault),
                    "--statement",
                    statement,
                    "--source-id",
                    source["id"],
                    "--locator",
                    locator,
                )["claim"]
            )
        select_node = command(
            "node",
            "add",
            "--vault",
            str(vault),
            "--title",
            "SELECT 与 WHERE",
            "--knowledge-type",
            "procedure",
            "--claim",
            claims[0]["id"],
            "--outcome",
            "独立写出筛选查询",
        )["node"]
        group_node = command(
            "node",
            "add",
            "--vault",
            str(vault),
            "--title",
            "GROUP BY 与聚合",
            "--knowledge-type",
            "concept",
            "--claim",
            claims[0]["id"],
            "--claim",
            claims[1]["id"],
            "--prerequisite",
            select_node["id"],
            "--outcome",
            "解释并写出分组聚合查询",
        )["node"]
        command(
            "node",
            "add",
            "--vault",
            str(vault),
            "--title",
            "窗口函数",
            "--knowledge-type",
            "mental-model",
            "--claim",
            claims[1]["id"],
            "--prerequisite",
            group_node["id"],
            "--outcome",
            "区分分组与窗口计算",
        )
        command("map", "render", "--vault", str(vault))
        plan = command(
            "plan",
            "build",
            "--vault",
            str(vault),
            "--weeks",
            "4",
            "--sessions-per-week",
            "5",
            "--minutes",
            "30",
        )["plan"]
        session = command(
            "session", "start", "--vault", str(vault), "--node-id", group_node["id"]
        )["session"]
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
            "求每个客户的订单总额，并解释为什么要使用 GROUP BY。",
            "--answer",
            "SELECT customer_id, SUM(amount) FROM orders GROUP BY customer_id; 因为要按客户分别聚合。",
        )["answer"]
        command(
            "session",
            "grade",
            "--vault",
            str(vault),
            "--answer-id",
            answer["id"],
            "--score",
            "0.84",
            "--feedback",
            "查询和分组理由正确。",
            "--correction",
            "补充非聚合选择列必须能确定每组唯一值的边界。",
            "--claim",
            claims[0]["id"],
            "--claim",
            claims[1]["id"],
            "--retrieval",
            "0.90",
            "--accuracy",
            "0.92",
            "--transfer",
            "0.78",
        )
        question = command(
            "session",
            "question",
            "--vault",
            str(vault),
            "--session-id",
            session["id"],
            "--question",
            "为什么 customer_id 必须出现在 GROUP BY？",
        )["question"]
        explanation = command(
            "session",
            "explain",
            "--vault",
            str(vault),
            "--question-id",
            question["id"],
            "--response",
            "分组后每组必须对应一个确定的 customer_id，否则结果行没有唯一客户值。",
            "--claim",
            claims[2]["id"],
            "--check-question",
            "如果还要按月份聚合，你会改哪两处？先用自己的话回答。",
        )["explanation"]
        check = command(
            "session",
            "answer",
            "--vault",
            str(vault),
            "--session-id",
            session["id"],
            "--explanation-id",
            explanation["id"],
            "--kind",
            "application",
            "--question",
            explanation["check_question"],
            "--answer",
            "SELECT 增加月份表达式，GROUP BY 也增加同一个月份表达式。",
        )["answer"]
        command(
            "session",
            "grade",
            "--vault",
            str(vault),
            "--answer-id",
            check["id"],
            "--score",
            "0.90",
            "--feedback",
            "能把分组边界迁移到二维分组。",
            "--correction",
            "实际查询时保持 SELECT 与 GROUP BY 的月份表达式一致。",
            "--claim",
            claims[2]["id"],
            "--retrieval",
            "0.88",
            "--accuracy",
            "0.92",
            "--transfer",
            "0.90",
        )
        command(
            "session",
            "finish",
            "--vault",
            str(vault),
            "--session-id",
            session["id"],
            "--minutes",
            "28",
            "--reflection",
            "每个结果行必须能对应确定的分组键。",
            "--confidence",
            "0.76",
        )
        report = command("report", "daily", "--vault", str(vault))["report"]
        state = json.loads((vault / ".kongzi" / "state.json").read_text(encoding="utf-8"))
        node_state = state["nodes"][group_node["id"]]
        return {
            "claim_short": claims[2]["id"][:12],
            "plan_sessions": len(plan["sessions"]),
            "minutes": report["minutes"],
            "graded": report["answers_graded"],
            "questions": report["learner_questions_answered"],
            "node_level": node_state["mastery"]["level"],
            "node_status": node_state["status"],
        }


def render_frames(data: dict[str, Any]) -> list[Image.Image]:
    scenes: list[Callable[[float, dict[str, Any]], Image.Image]] = [
        scene_intro,
        scene_profile,
        scene_sources,
        scene_roadmap,
        scene_study,
        scene_question,
        scene_review,
        scene_outro,
    ]
    frames: list[Image.Image] = []
    scene_frames = 17
    hold_frames = 3
    transition_frames = 4
    for index, scene in enumerate(scenes):
        current = [scene(step / (scene_frames - 1), data) for step in range(scene_frames)]
        frames.extend(current)
        frames.extend([current[-1]] * hold_frames)
        if index < len(scenes) - 1:
            next_first = scenes[index + 1](0.08, data)
            for step in range(1, transition_frames + 1):
                frames.append(
                    Image.blend(
                        current[-1],
                        next_first,
                        ease(step / (transition_frames + 1)),
                    )
                )
    return frames


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ROOT / "assets" / "demo.gif"))
    args = parser.parse_args()
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    data = build_demo_data()
    rgb_frames = render_frames(data)

    # Build one global palette from the final state of every scene.
    atlas = Image.new("RGB", (WIDTH, HEIGHT), BG)
    finals = [
        scene(1.0, data).resize((WIDTH // 4, HEIGHT // 2), Image.Resampling.LANCZOS)
        for scene in (
            scene_intro,
            scene_profile,
            scene_sources,
            scene_roadmap,
            scene_study,
            scene_question,
            scene_review,
            scene_outro,
        )
    ]
    for index, sample in enumerate(finals):
        atlas.paste(sample, ((index % 4) * WIDTH // 4, (index // 4) * HEIGHT // 2))
    palette = atlas.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    frames = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in rgb_frames]
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0,
        optimize=True,
        disposal=1,
    )
    print(
        json.dumps(
            {
                "output": str(output),
                "frames": len(frames),
                "duration_seconds": round(len(frames) / 10, 1),
                "real_run": data,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
