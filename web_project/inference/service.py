import threading
from collections import OrderedDict
from pathlib import Path

from django.conf import settings

from inference.model_profiles import get_model_profile
from modelYolo.models import YoloModel


def _as_list(value):
    if hasattr(value, "detach"):
        value = value.detach()
    if hasattr(value, "cpu"):
        value = value.cpu()
    if hasattr(value, "tolist"):
        return value.tolist()
    return list(value)


class InferenceService:
    _cache = OrderedDict()
    _cache_lock = threading.RLock()

    def __init__(self, model_loader=None):
        self.model_loader = model_loader or self._default_loader

    @classmethod
    def clear_cache(cls):
        with cls._cache_lock:
            cls._cache.clear()

    @staticmethod
    def _default_loader(path):
        from ultralytics import YOLO

        return YOLO(str(path))

    @staticmethod
    def _weights_path(model):
        root = Path(settings.MODELS_ROOT).resolve()
        candidate = (root / Path(model.file_path).name).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise ValueError("Model path escapes MODEL_STORAGE_ROOT.") from exc
        if not candidate.is_file():
            raise FileNotFoundError("Configured model weights are unavailable.")
        return candidate

    def _get_model(self, model_id):
        record = YoloModel.objects.get(pk=model_id)
        weights_path = self._weights_path(record)
        cache_key = (record.pk, record.version, str(weights_path), weights_path.stat().st_mtime_ns)
        with self._cache_lock:
            cached = self._cache.get(cache_key)
            if cached is not None:
                self._cache.move_to_end(cache_key)
                return record, cached
            loaded = self.model_loader(weights_path)
            self._cache[cache_key] = loaded
            max_entries = max(int(getattr(settings, "MODEL_CACHE_SIZE", 2)), 1)
            while len(self._cache) > max_entries:
                self._cache.popitem(last=False)
            return record, loaded

    @staticmethod
    def _serialize_result(result, *, frame=None, label_map=None):
        boxes = getattr(result, "boxes", None)
        if boxes is None:
            return []
        classes = _as_list(boxes.cls)
        confidences = _as_list(boxes.conf)
        coordinates = _as_list(boxes.xyxy)
        names = getattr(result, "names", {})
        detections = []
        for index, raw_class_id in enumerate(classes):
            class_id = int(raw_class_id)
            raw_label = (
                names.get(class_id, str(class_id)) if isinstance(names, dict) else names[class_id]
            )
            raw_label = str(raw_label)
            label = (label_map or {}).get(raw_label, raw_label)
            detection = {
                "label": label,
                "classId": class_id,
                "confidence": round(float(confidences[index]), 6),
                "box": [round(float(value), 3) for value in coordinates[index]],
            }
            if label != raw_label:
                detection["rawLabel"] = raw_label
            if frame is not None:
                detection["frame"] = frame
            detections.append(detection)
        return detections

    @staticmethod
    def _summarize(detections):
        labels = []
        for detection in detections:
            label = detection["label"]
            if not labels or labels[-1] != label:
                labels.append(label)
        confidence = (
            round(sum(item["confidence"] for item in detections) / len(detections), 6)
            if detections
            else None
        )
        return {
            "detections": detections,
            "labels": labels,
            "sentence": " ".join(labels),
            "confidence": confidence,
        }

    def predict_image(self, model_id, image_path, *, iou, conf):
        import numpy as np
        from PIL import Image

        record, model = self._get_model(model_id)
        profile = get_model_profile(record.file_path) or {}
        with Image.open(image_path) as image:
            rgb = np.asarray(image.convert("RGB"))
        source = np.ascontiguousarray(rgb[..., ::-1])
        results = model.predict(
            source=source,
            iou=float(iou),
            conf=float(conf),
            save=False,
            verbose=False,
        )
        first = results[0] if results else None
        detections = (
            self._serialize_result(first, label_map=profile.get("labelMap"))
            if first is not None
            else []
        )
        return self._summarize(detections)

    def predict_video(self, model_id, video_path, *, iou, conf):
        record, model = self._get_model(model_id)
        profile = get_model_profile(record.file_path) or {}
        results = model.predict(
            source=str(video_path),
            iou=float(iou),
            conf=float(conf),
            save=False,
            stream=True,
            verbose=False,
        )
        detections = []
        frame_count = 0
        for frame_count, result in enumerate(results, start=1):
            detections.extend(
                self._serialize_result(
                    result,
                    frame=frame_count,
                    label_map=profile.get("labelMap"),
                )
            )
        summary = self._summarize(detections)
        summary["frames"] = frame_count
        return summary
