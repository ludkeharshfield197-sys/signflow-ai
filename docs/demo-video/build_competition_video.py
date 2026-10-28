from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[2]
DEMO_DIR = Path(__file__).resolve().parent
DESKTOP_FRAMES = DEMO_DIR / "frames-2026-08-25"
MOBILE_FRAMES = DEMO_DIR / "mobile-frames-2026-08-25"
OUTPUT = DEMO_DIR / "SignFlow-AI-competition-full-demo-2026-08-25.mp4"
COVER = DEMO_DIR / "SignFlow-AI-competition-demo-cover.png"
MANIFEST = DEMO_DIR / "SignFlow-AI-competition-full-demo-2026-08-25.json"

WIDTH = 1280
HEIGHT = 720
FPS = 24
SOURCE_FPS = 6
SOURCE_REPEAT = FPS // SOURCE_FPS

FONT_REGULAR = Path(r"C:\Windows\Fonts\msyh.ttc")
FONT_BOLD = Path(r"C:\Windows\Fonts\msyhbd.ttc")


@dataclass(frozen=True)
class FrameRange:
    source: str
    start: int
    end: int
    label: str

    @property
    def count(self) -> int:
        return self.end - self.start + 1


DESKTOP_SECTIONS: list[tuple[str, str, list[FrameRange]]] = [
    (
        "01",
        "产品导览与官方样例",
        [
            FrameRange("desktop", 0, 92, "多场景产品导览"),
            FrameRange("desktop", 126, 288, "识别结果与沟通闭环"),
        ],
    ),
    (
        "02",
        "Web 工作台与双模型识别",
        [
            FrameRange("desktop", 289, 314, "安全登录"),
            FrameRange("desktop", 340, 454, "运营概览与输入配置"),
            FrameRange("desktop", 535, 551, "ASL 真实图片结果"),
            FrameRange("desktop", 674, 817, "实时样例与结果中心"),
        ],
    ),
    (
        "03",
        "可信结果与版本追溯",
        [FrameRange("desktop", 901, 1050, "CSL 真实图片、双方确认与版本对比")],
    ),
    (
        "04",
        "数据洞察与模型评测",
        [FrameRange("desktop", 1051, 1203, "真实指标、CSL/ASL 评测卡与能力边界")],
    ),
    (
        "05",
        "隐私、治理与系统运行",
        [FrameRange("desktop", 1204, 1525, "账户安全、管理后台、官网与隐私页面")],
    ),
]

MOBILE_RANGES = [
    FrameRange("mobile", 0, 119, "登录、运营首页与三种输入模式"),
    FrameRange("mobile", 156, 303, "真实 CSL 推理、追溯与双方确认"),
    FrameRange("mobile", 304, 391, "记录筛选、服务设置与无障碍模式"),
]


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REGULAR), size=size)


def gradient_background(start: tuple[int, int, int], end: tuple[int, int, int]) -> Image.Image:
    top = np.array(start, dtype=np.float32)
    bottom = np.array(end, dtype=np.float32)
    ratio = np.linspace(0, 1, HEIGHT, dtype=np.float32)[:, None]
    pixels = top[None, :] * (1 - ratio) + bottom[None, :] * ratio
    pixels = np.repeat(pixels[:, None, :], WIDTH, axis=1).astype(np.uint8)
    return Image.fromarray(pixels)


def add_ambient_shapes(image: Image.Image, *, dark: bool) -> None:
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    if dark:
        draw.ellipse((860, -210, 1430, 360), fill=(114, 92, 255, 42))
        draw.ellipse((-250, 430, 420, 1100), fill=(36, 187, 165, 28))
        draw.rounded_rectangle((820, 470, 1210, 660), 48, fill=(255, 255, 255, 12))
    else:
        draw.ellipse((930, -260, 1460, 270), fill=(91, 91, 214, 24))
        draw.ellipse((-240, 450, 370, 1060), fill=(14, 147, 132, 18))
    image.alpha_composite(overlay)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, text_font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for character in text:
        candidate = current + character
        box = draw.textbbox((0, 0), candidate, font=text_font)
        if current and box[2] - box[0] > width:
            lines.append(current)
            current = character
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def title_card() -> Image.Image:
    image = gradient_background((11, 20, 38), (28, 25, 68)).convert("RGBA")
    add_ambient_shapes(image, dark=True)
    draw = ImageDraw.Draw(image)
    purple = (143, 132, 255, 255)
    teal = (77, 214, 190, 255)

    draw.rounded_rectangle((76, 62, 370, 108), 23, fill=(31, 41, 64, 255), outline=(67, 78, 102, 255), width=1)
    draw.ellipse((94, 77, 110, 93), fill=teal)
    draw.text((122, 72), "无界手语  SignFlow AI", font=font(22, bold=True), fill="white")
    draw.text((76, 170), "让手语沟通自然进入", font=font(56, bold=True), fill="white")
    draw.text((76, 242), "每一次服务", font=font(72, bold=True), fill=purple)
    draw.text((80, 350), "多模态手语沟通平台 · 完整功能演示", font=font(28), fill=(221, 226, 240, 255))

    pills = ["CSL / ASL 双模型", "图片 · 视频 · 实时", "Web · H5 · 小程序"]
    x = 78
    for pill in pills:
        box = draw.textbbox((0, 0), pill, font=font(19, bold=True))
        pill_width = box[2] - box[0] + 38
        draw.rounded_rectangle((x, 430, x + pill_width, 474), 22, fill=(38, 45, 72, 255), outline=(78, 88, 118, 255), width=1)
        draw.text((x + 19, 440), pill, font=font(19, bold=True), fill=(245, 247, 255, 255))
        x += pill_width + 16

    draw.line((78, 568, 1202, 568), fill=(255, 255, 255, 34), width=1)
    draw.text((78, 600), "本地模型真实推理", font=font(18, bold=True), fill=teal)
    draw.text((303, 600), "结果可追溯", font=font(18, bold=True), fill=teal)
    draw.text((462, 600), "隐私优先", font=font(18, bold=True), fill=teal)
    draw.text((1034, 600), "2026.08.25", font=font(18), fill=(168, 177, 198, 255))
    return image.convert("RGB")


def chapter_card(number: str, title: str, subtitle: str) -> Image.Image:
    image = gradient_background((246, 247, 252), (234, 236, 251)).convert("RGBA")
    add_ambient_shapes(image, dark=False)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((76, 72, 196, 192), 30, fill=(91, 91, 214, 255))
    draw.text((103, 88), number, font=font(54, bold=True), fill="white")
    draw.text((76, 250), title, font=font(49, bold=True), fill=(16, 24, 40, 255))
    y = 328
    for line in wrap_text(draw, subtitle, font(25), 980):
        draw.text((80, y), line, font=font(25), fill=(71, 84, 103, 255))
        y += 41
    draw.rounded_rectangle((78, 505, 312, 550), 22, fill=(91, 91, 214, 20))
    draw.text((98, 516), "SIGNFLOW AI DEMO", font=font(16, bold=True), fill=(91, 91, 214, 255))
    draw.line((78, 616, 1202, 616), fill=(91, 91, 214, 50), width=2)
    draw.line((78, 616, 78 + int(1124 * int(number) / 6), 616), fill=(91, 91, 214, 255), width=4)
    return image.convert("RGB")


def end_card() -> Image.Image:
    image = gradient_background((12, 21, 39), (31, 28, 75)).convert("RGBA")
    add_ambient_shapes(image, dark=True)
    draw = ImageDraw.Draw(image)
    draw.text((80, 92), "无界手语  SignFlow AI", font=font(24, bold=True), fill=(143, 132, 255, 255))
    draw.text((80, 205), "看见表达，连接服务", font=font(62, bold=True), fill="white")
    draw.text((82, 305), "从真实视觉推理到可信沟通闭环", font=font(30), fill=(219, 224, 240, 255))
    points = ["CSL / ASL 本地模型", "多端统一任务中心", "结果、参数与版本全程可追溯"]
    y = 405
    for point in points:
        draw.ellipse((84, y + 9, 96, y + 21), fill=(77, 214, 190, 255))
        draw.text((116, y), point, font=font(22, bold=True), fill=(241, 244, 252, 255))
        y += 52
    draw.text((972, 626), "SIGNFLOW AI", font=font(19, bold=True), fill=(166, 175, 198, 255))
    return image.convert("RGB")


def fit_desktop(source: Image.Image) -> Image.Image:
    canvas = Image.new("RGB", (WIDTH, HEIGHT), "#0b1220")
    frame = source.convert("RGB")
    frame.thumbnail((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    canvas.paste(frame, ((WIDTH - frame.width) // 2, (HEIGHT - frame.height) // 2))
    return canvas


def mobile_context(index: int) -> tuple[str, str, list[str]]:
    if index < 32:
        return "安全登录", "同一账号，跨端同步", ["密码不写入 URL 或日志", "账号与结果按权限隔离"]
    if index < 80:
        return "移动运营首页", "真实任务一目了然", ["今日任务、成功率与服务状态", "最近结果即时同步"]
    if index < 156:
        return "多模态输入", "图片、视频与实时模式", ["CSL / ASL 模型可配置", "输入默认不进入训练集"]
    if index < 224:
        return "真实 CSL 推理", "本地模型生成真实结果", ["安全上传、模型推理、结果生成", "置信度与标签同步展示"]
    if index < 304:
        return "结果追溯", "从原始媒体到双方确认", ["文件哈希与识别参数留存", "结果版本支持复核"]
    if index < 348:
        return "识别记录", "按输入类型快速筛选", ["图片与视频结果统一管理", "同一账号多端可见"]
    return "隐私与无障碍", "适配真实服务场景", ["大字与高对比模式", "数据保留策略清晰可见"]


def compose_mobile(source: Image.Image, index: int) -> Image.Image:
    canvas = gradient_background((246, 247, 252), (233, 235, 250)).convert("RGBA")
    add_ambient_shapes(canvas, dark=False)
    draw = ImageDraw.Draw(canvas)
    title, subtitle, bullets = mobile_context(index)

    draw.rounded_rectangle((72, 70, 286, 112), 21, fill=(91, 91, 214, 22))
    draw.text((92, 80), "手机端 H5 / 小程序", font=font(17, bold=True), fill=(91, 91, 214, 255))
    draw.text((72, 178), title, font=font(48, bold=True), fill=(16, 24, 40, 255))
    draw.text((76, 254), subtitle, font=font(26), fill=(71, 84, 103, 255))
    y = 345
    for bullet in bullets:
        draw.ellipse((79, y + 9, 91, y + 21), fill=(14, 147, 132, 255))
        draw.text((112, y), bullet, font=font(21, bold=True), fill=(52, 64, 84, 255))
        y += 60
    draw.line((76, 530, 690, 530), fill=(91, 91, 214, 55), width=2)
    draw.text((76, 560), "真实模型 · 真实任务 · 真实结果", font=font(20, bold=True), fill=(91, 91, 214, 255))
    draw.text((76, 605), "SignFlow AI 多端交付能力", font=font(18), fill=(102, 112, 133, 255))

    phone = source.convert("RGB")
    phone.thumbnail((336, 680), Image.Resampling.LANCZOS)
    phone_x = 848 + (336 - phone.width) // 2
    phone_y = (HEIGHT - phone.height) // 2

    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((phone_x - 14, phone_y - 14, phone_x + phone.width + 14, phone_y + phone.height + 14), 34, fill=(16, 24, 40, 70))
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    canvas.alpha_composite(shadow)
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((phone_x - 9, phone_y - 9, phone_x + phone.width + 9, phone_y + phone.height + 9), 28, fill=(255, 255, 255, 255), outline=(207, 211, 231, 255), width=2)
    canvas.paste(phone, (phone_x, phone_y))
    return canvas.convert("RGB")


def write_image(writer: cv2.VideoWriter, image: Image.Image, repeats: int) -> int:
    bgr = cv2.cvtColor(np.asarray(image, dtype=np.uint8), cv2.COLOR_RGB2BGR)
    for _ in range(repeats):
        writer.write(bgr)
    return repeats


def write_still(writer: cv2.VideoWriter, image: Image.Image, seconds: float) -> int:
    return write_image(writer, image, round(seconds * FPS))


def write_range(writer: cv2.VideoWriter, frame_range: FrameRange) -> int:
    folder = DESKTOP_FRAMES if frame_range.source == "desktop" else MOBILE_FRAMES
    written = 0
    for index in range(frame_range.start, frame_range.end + 1):
        path = folder / f"{index:05d}.png"
        if not path.exists():
            raise FileNotFoundError(path)
        with Image.open(path) as source:
            frame = fit_desktop(source) if frame_range.source == "desktop" else compose_mobile(source, index)
        written += write_image(writer, frame, SOURCE_REPEAT)
    return written


def main() -> None:
    cover = title_card()
    cover.save(COVER, optimize=True)

    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    writer = cv2.VideoWriter(str(OUTPUT), fourcc, FPS, (WIDTH, HEIGHT))
    if not writer.isOpened():
        raise RuntimeError("OpenCV could not open the MP4 writer with the H.264/AVC codec.")

    total_frames = 0
    timeline: list[dict[str, object]] = []

    def add_timeline(label: str, start_frame: int, end_frame: int) -> None:
        timeline.append(
            {
                "label": label,
                "startSeconds": round(start_frame / FPS, 2),
                "endSeconds": round(end_frame / FPS, 2),
            }
        )

    start = total_frames
    total_frames += write_still(writer, cover, 3.0)
    add_timeline("片头", start, total_frames)
    print("Rendered cover", flush=True)

    all_ranges: list[FrameRange] = []
    for number, title, ranges in DESKTOP_SECTIONS:
        start = total_frames
        chapter_subtitle = " · ".join(frame_range.label for frame_range in ranges)
        total_frames += write_still(writer, chapter_card(number, title, chapter_subtitle), 1.7)
        add_timeline(f"章节 {number}：{title}", start, total_frames)
        for frame_range in ranges:
            start = total_frames
            total_frames += write_range(writer, frame_range)
            add_timeline(frame_range.label, start, total_frames)
            all_ranges.append(frame_range)
        print(f"Rendered desktop chapter {number}: {title}", flush=True)

    start = total_frames
    total_frames += write_still(
        writer,
        chapter_card("06", "手机端 H5 与小程序体验", "安全登录 · 真实推理 · 结果追溯 · 记录筛选 · 无障碍显示"),
        2.0,
    )
    add_timeline("章节 06：手机端 H5 与小程序体验", start, total_frames)
    for frame_range in MOBILE_RANGES:
        start = total_frames
        total_frames += write_range(writer, frame_range)
        add_timeline(frame_range.label, start, total_frames)
        all_ranges.append(frame_range)
    print("Rendered mobile chapter", flush=True)

    start = total_frames
    total_frames += write_still(writer, end_card(), 3.0)
    add_timeline("片尾", start, total_frames)
    writer.release()

    capture = cv2.VideoCapture(str(OUTPUT))
    if not capture.isOpened():
        raise RuntimeError("The generated MP4 could not be reopened for verification.")
    verified_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    verified_fps = float(capture.get(cv2.CAP_PROP_FPS))
    verified_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    verified_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    capture.release()
    if verified_frames <= 0 or verified_width != WIDTH or verified_height != HEIGHT:
        raise RuntimeError("The generated MP4 failed the frame-count or resolution check.")

    manifest = {
        "title": "无界手语 SignFlow AI 完整功能演示",
        "generatedAt": "2026-08-25",
        "output": str(OUTPUT),
        "codec": "H.264/AVC (avc1)",
        "resolution": f"{WIDTH}x{HEIGHT}",
        "fps": verified_fps,
        "frameCount": verified_frames,
        "durationSeconds": round(verified_frames / verified_fps, 2),
        "silent": True,
        "selectedRanges": [frame_range.__dict__ for frame_range in all_ranges],
        "excludedDesktopRanges": [[93, 125], [315, 339], [455, 534], [552, 673], [818, 900]],
        "excludedMobileRanges": [[120, 155]],
        "timeline": timeline,
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
