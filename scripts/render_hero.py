#!/usr/bin/env python3
"""Create a small looping README hero GIF from assets/hero.png."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from PIL import Image, ImageEnhance
except ImportError as exc:  # pragma: no cover - developer-only asset tool
    raise SystemExit("Hero rendering needs Pillow: python3 -m pip install Pillow") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="assets/hero.png")
    parser.add_argument("--output", default="assets/hero.gif")
    args = parser.parse_args()
    source = Image.open(args.input).convert("RGB")
    target_size = (960, 540)
    frames = []
    count = 20
    for index in range(count):
        phase = index if index <= count // 2 else count - index
        zoom = 1 + phase * 0.0028
        crop_width = round(source.width / zoom)
        crop_height = round(source.height / zoom)
        left = (source.width - crop_width) // 2
        top = (source.height - crop_height) // 2
        frame = source.crop((left, top, left + crop_width, top + crop_height))
        frame = frame.resize(target_size, Image.Resampling.LANCZOS)
        frame = ImageEnhance.Brightness(frame).enhance(1 + phase * 0.002)
        frames.append(frame.quantize(colors=128, method=Image.Quantize.MEDIANCUT))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=150,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
