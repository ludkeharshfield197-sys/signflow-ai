"""Benchmark bundled models on curated product assets without training.

This script measures the full local prediction path after one warm-up inference.
It reports label-presence regression metrics, average image latency and decoded
video throughput. Detection mAP is intentionally evaluated separately on
bounding-box datasets with ``YOLO.val``.
"""

import argparse
import json
import os
import platform
import sys
import time
from datetime import date
from pathlib import Path

# Benchmarking must be read-only with respect to the Python environment.
os.environ.setdefault("YOLO_AUTOINSTALL", "false")

WEB_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = WEB_ROOT.parent
if str(WEB_ROOT) not in sys.path:
    sys.path.insert(0, str(WEB_ROOT))

from inference.evaluation import presence_metrics  # noqa: E402
from inference.model_profiles import get_model_profile  # noqa: E402


def _labels_from_result(result, label_map):
    boxes = getattr(result, "boxes", None)
    if boxes is None:
        return []
    class_ids = boxes.cls.detach().cpu().tolist()
    names = getattr(result, "names", {})
    labels = []
    for raw_class_id in class_ids:
        class_id = int(raw_class_id)
        raw_label = names.get(class_id, str(class_id))
        labels.append(label_map.get(str(raw_label), str(raw_label)))
    return labels


def _asset_specs(manifest):
    if "positiveAssets" in manifest:
        rows = [
            {
                "path": item["path"],
                "mode": item["type"],
                "expected": item["expectedLabels"],
            }
            for item in manifest["positiveAssets"]
        ]
        rows.extend(
            {
                "path": item["path"],
                "mode": item["type"],
                "expected": item["expectedLabels"],
            }
            for item in manifest.get("negativeAssets", [])
        )
        return rows
    return [
        {
            "path": item["path"],
            "mode": item["mode"],
            "expected": item["expectedSentence"].split(),
        }
        for item in manifest["assets"]
    ]


def benchmark_model(model, profile, manifest_path):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    asset_root = manifest_path.parent
    label_map = profile.get("labelMap", {})
    specs = _asset_specs(manifest)
    first_image = next(item for item in specs if item["mode"] == "image")
    model.predict(
        source=str(asset_root / first_image["path"]),
        imgsz=640,
        conf=0.45,
        iou=0.5,
        save=False,
        verbose=False,
    )

    samples = []
    image_latencies = []
    video_seconds = 0.0
    video_frames = 0
    for spec in specs:
        source = asset_root / spec["path"]
        started = time.perf_counter()
        results = model.predict(
            source=str(source),
            imgsz=640,
            conf=0.45,
            iou=0.5,
            save=False,
            stream=spec["mode"] == "video",
            verbose=False,
        )
        predicted = []
        frames = 0
        for frames, result in enumerate(results, start=1):
            predicted.extend(_labels_from_result(result, label_map))
        elapsed = time.perf_counter() - started
        if spec["mode"] == "video":
            video_seconds += elapsed
            video_frames += frames
        else:
            image_latencies.append(elapsed * 1000)
        samples.append(
            {
                "asset": spec["path"],
                "expected": spec["expected"],
                "predicted": list(dict.fromkeys(predicted)),
                "elapsedMs": round(elapsed * 1000, 2),
                "frames": frames,
            }
        )

    return {
        "regressionSet": {
            "sampleCount": len(samples),
            "metrics": presence_metrics(samples),
            "samples": samples,
        },
        "performance": {
            "averageImageLatencyMs": (
                round(sum(image_latencies) / len(image_latencies), 2) if image_latencies else None
            ),
            "videoFps": round(video_frames / video_seconds, 2) if video_seconds else None,
            "videoFrames": video_frames,
            "videoSeconds": round(video_seconds, 2),
        },
    }


def hardware_summary():
    processor = platform.processor() or os.getenv("PROCESSOR_IDENTIFIER", "unknown CPU")
    return {
        "processor": processor,
        "platform": platform.platform(),
        "python": platform.python_version(),
        "device": "CPU",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models-root", type=Path, default=WEB_ROOT / "model")
    parser.add_argument(
        "--assets-root",
        type=Path,
        default=REPO_ROOT / "sign" / "public" / "test-assets",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    from ultralytics import YOLO

    configurations = {
        "asl": {
            "weights": "ASl-v8.pt",
            "manifest": args.assets_root / "real-recognition" / "manifest.json",
        },
        "csl": {
            "weights": "csl.pt",
            "manifest": args.assets_root / "csl-recognition" / "manifest.json",
        },
    }
    report = {
        "evaluatedAt": date.today().isoformat(),
        "hardware": hardware_summary(),
        "models": {},
    }
    for key, configuration in configurations.items():
        weights = args.models_root / configuration["weights"]
        profile = get_model_profile(weights.name) or {}
        report["models"][key] = benchmark_model(
            YOLO(str(weights)),
            profile,
            configuration["manifest"],
        )

    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
