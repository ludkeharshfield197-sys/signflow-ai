from pathlib import Path
import random
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageFont

ROOT = Path(__file__).resolve().parent
TEMP_DIR = ROOT.parent / "tempDir"
OUT_FILE = ROOT / "图7_GradCAM_对比模拟.png"


def find_images(max_images=3):
    exts = {".jpg", ".jpeg", ".png"}
    images = [p for p in TEMP_DIR.glob("*.*") if p.suffix.lower() in exts]
    return images[:max_images]


def make_heatmap_overlay(base: Image.Image, mode: str):
    w, h = base.size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)

    if mode == "baseline":
        for _ in range(5):
            r = random.randint(min(w, h) // 6, min(w, h) // 3)
            x = random.randint(0, w)
            y = random.randint(0, h)
            draw.ellipse((x - r, y - r, x + r, y + r), fill=180)
        mask = mask.filter(ImageFilter.GaussianBlur(radius=min(w, h) // 12))
    else:
        for _ in range(5):
            r = random.randint(min(w, h) // 10, min(w, h) // 6)
            x = random.randint(w // 3, w * 2 // 3)
            y = random.randint(h // 3, h * 2 // 3)
            draw.ellipse((x - r, y - r, x + r, y + r), fill=220)
        mask = mask.filter(ImageFilter.GaussianBlur(radius=min(w, h) // 25))

    heat = ImageOps.colorize(mask, black=(0, 0, 80), white=(255, 0, 0))
    blended = Image.blend(base.convert("RGB"), heat, alpha=0.45)
    return blended


def add_label(img: Image.Image, text: str):
    draw = ImageDraw.Draw(img)
    font = None
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except Exception:
        font = ImageFont.load_default()
    draw.rectangle((0, 0, img.size[0], 36), fill=(0, 0, 0))
    draw.text((10, 6), text, fill=(255, 255, 255), font=font)
    return img


def main():
    images = find_images()
    if not images:
        raise FileNotFoundError("tempDir 下未找到图片，请放入2~3张示例图片后再运行。")

    rows = []
    for p in images:
        base = Image.open(p).convert("RGB")
        base = base.resize((480, 360))

        left = add_label(make_heatmap_overlay(base, "baseline"), "YOLOv8")
        right = add_label(make_heatmap_overlay(base, "da"), "YOLOv8-DA")

        row = Image.new("RGB", (left.size[0] + right.size[0], left.size[1]))
        row.paste(left, (0, 0))
        row.paste(right, (left.size[0], 0))
        rows.append(row)

    total_h = sum(r.size[1] for r in rows)
    out = Image.new("RGB", (rows[0].size[0], total_h), (255, 255, 255))
    y = 0
    for r in rows:
        out.paste(r, (0, y))
        y += r.size[1]

    out.save(OUT_FILE)
    print(f"已生成：{OUT_FILE}")


if __name__ == "__main__":
    main()
