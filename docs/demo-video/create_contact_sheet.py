from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a numbered contact sheet from PNG frames.")
    parser.add_argument("frames", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--step", type=int, default=20)
    parser.add_argument("--columns", type=int, default=5)
    parser.add_argument("--width", type=int, default=240)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = sorted(args.frames.glob("*.png"))[:: args.step]
    if not paths:
        raise SystemExit(f"No PNG frames found in {args.frames}")

    with Image.open(paths[0]) as first:
        aspect = first.height / first.width
    thumb_height = round(args.width * aspect)
    label_height = 28
    rows = (len(paths) + args.columns - 1) // args.columns
    sheet = Image.new("RGB", (args.columns * args.width, rows * (thumb_height + label_height)), "#101828")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=18)

    for index, path in enumerate(paths):
        with Image.open(path) as source:
            thumb = source.convert("RGB")
            thumb.thumbnail((args.width, thumb_height), Image.Resampling.LANCZOS)
        column = index % args.columns
        row = index // args.columns
        x = column * args.width + (args.width - thumb.width) // 2
        y = row * (thumb_height + label_height)
        sheet.paste(thumb, (x, y))
        draw.text((column * args.width + 8, y + thumb_height + 4), path.stem, fill="white", font=font)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output, optimize=True)
    print(args.output)


if __name__ == "__main__":
    main()
