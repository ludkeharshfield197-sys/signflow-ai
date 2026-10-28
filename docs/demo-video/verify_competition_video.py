from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np


DEMO_DIR = Path(__file__).resolve().parent
VIDEO = DEMO_DIR / "SignFlow-AI-competition-full-demo-2026-08-25.mp4"
OUTPUT_DIR = DEMO_DIR / "verification-frames"
REPORT = DEMO_DIR / "SignFlow-AI-competition-full-demo-2026-08-25-verification.json"
EXPECTED_WIDTH = 1280
EXPECTED_HEIGHT = 720
EXPECTED_FPS = 24.0


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    if not VIDEO.exists():
        raise SystemExit(f"Missing video: {VIDEO}")

    capture = cv2.VideoCapture(str(VIDEO))
    if not capture.isOpened():
        raise SystemExit("OpenCV could not decode the generated video.")

    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = float(capture.get(cv2.CAP_PROP_FPS))
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = frame_count / fps if fps else 0

    assert width == EXPECTED_WIDTH, (width, EXPECTED_WIDTH)
    assert height == EXPECTED_HEIGHT, (height, EXPECTED_HEIGHT)
    assert abs(fps - EXPECTED_FPS) < 0.01, (fps, EXPECTED_FPS)
    assert frame_count > 6000, frame_count
    assert 265 <= duration <= 280, duration

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sample_seconds = [1, 15, 55, 110, 140, 175, 220, 245, 268, 272]
    samples = []
    for second in sample_seconds:
        capture.set(cv2.CAP_PROP_POS_MSEC, second * 1000)
        ok, frame = capture.read()
        assert ok and frame is not None, f"Could not decode frame at {second}s"
        mean = float(frame.mean())
        stddev = float(frame.std())
        assert mean > 12, f"Frame at {second}s is too dark: mean={mean:.2f}"
        assert stddev > 8, f"Frame at {second}s lacks visual detail: stddev={stddev:.2f}"
        output = OUTPUT_DIR / f"sample-{second:03d}s.png"
        assert cv2.imwrite(str(output), frame), output
        samples.append(
            {
                "second": second,
                "file": str(output),
                "mean": round(mean, 2),
                "stddev": round(stddev, 2),
            }
        )
    capture.release()

    file_size = VIDEO.stat().st_size
    assert file_size > 5 * 1024 * 1024, file_size
    report = {
        "video": str(VIDEO),
        "sha256": sha256(VIDEO),
        "sizeBytes": file_size,
        "resolution": [width, height],
        "fps": fps,
        "frameCount": frame_count,
        "durationSeconds": round(duration, 2),
        "decodeSamples": samples,
        "result": "passed",
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
