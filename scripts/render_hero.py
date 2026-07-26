#!/usr/bin/env python3
"""Render the Kongzi learning-philosophy loop as a compact README GIF."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
except ImportError as exc:  # pragma: no cover - developer-only asset tool
    raise SystemExit("Hero rendering needs Pillow: python3 -m pip install Pillow") from exc


ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 960, 540
INDIGO = (7, 17, 31)
INK = (236, 241, 235)
MUTED = (171, 187, 183)
JADE = (112, 225, 190)
GOLD = (239, 198, 111)

STAGES = (
    ("资料有据", "从可追溯的材料出发"),
    ("因材施教", "按目标、基础与时间规划"),
    ("学必有问", "先让学习者作答，再耐心讲解"),
    ("学而时习", "在将要遗忘时主动复习"),
    ("知行合一", "用迁移与作品证明掌握"),
)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("/System/Library/Fonts/STHeiti Medium.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for path in candidates:
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size=size, index=1 if bold else 0)
            except OSError:
                return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


TITLE = font(24, bold=True)
STAGE_TITLE = font(18, bold=True)
BODY = font(13)
SMALL = font(11)


def ease(value: float) -> float:
    return value * value * (3 - 2 * value)


def rgba_layer() -> Image.Image:
    return Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))


def add_focus_glow(frame: Image.Image, center: tuple[int, int], strength: float) -> None:
    glow = rgba_layer()
    draw = ImageDraw.Draw(glow)
    radius = 38 + round(12 * strength)
    x, y = center
    draw.ellipse(
        (x - radius, y - radius, x + radius, y + radius),
        fill=(*JADE, round(46 * strength)),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(22))
    frame.alpha_composite(glow)


def render_frame(base: Image.Image, frame_index: int, total_frames: int) -> Image.Image:
    frame = base.copy().convert("RGBA")
    shade = rgba_layer()
    shade_draw = ImageDraw.Draw(shade)
    shade_draw.rectangle((0, 0, WIDTH, 92), fill=(*INDIGO, 102))
    shade_draw.rectangle((0, 438, WIDTH, HEIGHT), fill=(*INDIGO, 210))
    frame.alpha_composite(shade)

    phase = frame_index / total_frames * len(STAGES)
    active = min(int(phase), len(STAGES) - 1)
    local = phase - int(phase)
    pulse = 0.5 + 0.5 * math.sin(local * math.tau)

    focus_centers = ((158, 162), (748, 174), (512, 334), (762, 360), (836, 382))
    add_focus_glow(frame, focus_centers[active], 0.55 + 0.45 * pulse)

    overlay = rgba_layer()
    draw = ImageDraw.Draw(overlay)
    draw.text((34, 24), "KONGZI · 孔子学习闭环", font=TITLE, fill=INK)
    draw.text(
        (36, 59),
        "有教无类 · 因材施教 · 学而时习 · 知行合一",
        font=BODY,
        fill=(*MUTED, 235),
    )

    rail_left, rail_right, rail_y = 44, WIDTH - 44, 474
    node_gap = (rail_right - rail_left) / (len(STAGES) - 1)
    draw.line((rail_left, rail_y, rail_right, rail_y), fill=(*MUTED, 90), width=2)

    completed_width = node_gap * (active + ease(local))
    draw.line(
        (rail_left, rail_y, rail_left + completed_width, rail_y),
        fill=(*JADE, 225),
        width=3,
    )

    for index, (label, _) in enumerate(STAGES):
        x = round(rail_left + node_gap * index)
        is_active = index == active
        is_done = index < active
        color = GOLD if is_active else JADE if is_done else MUTED
        radius = 7 + (round(2 * pulse) if is_active else 0)
        draw.ellipse(
            (x - radius, rail_y - radius, x + radius, rail_y + radius),
            fill=(*INDIGO, 255),
            outline=(*color, 255),
            width=3 if is_active else 2,
        )
        if is_done:
            draw.ellipse((x - 3, rail_y - 3, x + 3, rail_y + 3), fill=(*JADE, 255))
        label_box = draw.textbbox((0, 0), label, font=SMALL)
        label_width = label_box[2] - label_box[0]
        draw.text((x - label_width / 2, rail_y + 15), label, font=SMALL, fill=(*color, 245))

    for particle_index in range(4):
        progress = (local + particle_index / 4) % 1
        x = rail_left + node_gap * (active + progress)
        if active == len(STAGES) - 1:
            x = rail_left + node_gap * active
        alpha = round(200 * math.sin(progress * math.pi))
        draw.ellipse((x - 2, rail_y - 2, x + 2, rail_y + 2), fill=(*GOLD, alpha))

    title, subtitle = STAGES[active]
    reveal = ease(min(1.0, local * 2.8))
    card_width = 338
    card_x, card_y = WIDTH - card_width - 32, 28
    draw.rounded_rectangle(
        (card_x, card_y, card_x + card_width, card_y + 61),
        radius=13,
        fill=(*INDIGO, round(205 * reveal)),
        outline=(*GOLD, round(115 * reveal)),
        width=1,
    )
    draw.text((card_x + 18, card_y + 9), f"0{active + 1}  {title}", font=STAGE_TITLE, fill=(*GOLD, round(255 * reveal)))
    draw.text((card_x + 18, card_y + 36), subtitle, font=BODY, fill=(*INK, round(238 * reveal)))

    frame.alpha_composite(overlay)
    return frame.convert("RGB")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(ROOT / "assets" / "hero.png"))
    parser.add_argument("--output", default=str(ROOT / "assets" / "hero.gif"))
    args = parser.parse_args()

    source = Image.open(args.input).convert("RGB")
    base = ImageOps.fit(source, (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS)
    total_frames = 60
    rgb_frames = [render_frame(base, index, total_frames) for index in range(total_frames)]

    # A shared palette prevents distracting color flicker and keeps the README asset small.
    palette = rgb_frames[0].quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    frames = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in rgb_frames]
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=170,
        loop=0,
        optimize=True,
        disposal=1,
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
