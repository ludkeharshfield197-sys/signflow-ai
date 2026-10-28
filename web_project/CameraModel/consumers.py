from __future__ import annotations

import asyncio
import base64
import binascii
import json
import logging
import time
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from CameraModel.models import CameraDetection, CameraSession
from detections.models import DetectionJob
from inference.service import InferenceService
from modelYolo.models import YoloModel


logger = logging.getLogger(__name__)


def summarize_camera_results(results, *, duration_ms):
    labels = []
    detections = []
    confidences = []
    for frame_result in results:
        detections.extend(frame_result.get("detections") or [])
        confidence = frame_result.get("confidence")
        if confidence is not None:
            confidences.append(float(confidence))
        for label in frame_result.get("labels") or []:
            label_text = str(label)
            if label_text and (not labels or labels[-1] != label_text):
                labels.append(label_text)
    return {
        "detections": detections,
        "labels": labels,
        "sentence": " ".join(labels),
        "confidence": (
            round(sum(confidences) / len(confidences), 6) if confidences else None
        ),
        "frames": len(results),
        "durationMs": max(int(duration_ms), 0),
        "inputDurationMs": max(int(duration_ms), 1),
    }


@transaction.atomic
def create_camera_records(*, user, model_id, session_id, iou, confidence):
    model = YoloModel.objects.get(pk=model_id)
    if str(model.status).lower() not in {"正常", "active", "deployed", "ready"}:
        raise YoloModel.DoesNotExist
    session = CameraSession.objects.create(
        session_id=session_id,
        model=model,
        iou_threshold=iou,
        confidence_threshold=confidence,
        creator=user,
    )
    job = DetectionJob.objects.create(
        owner=user,
        mode=DetectionJob.Mode.LIVE,
        asset_key=f"users/{user.id}/camera-sessions/{session_id}",
        original_filename="\u5b9e\u65f6\u6444\u50cf\u5934",
        content_type="application/x-signflow-camera",
        model=model,
        model_snapshot={
            "id": model.id,
            "name": model.name,
            "version": model.version,
            "fileSize": model.size,
        },
        preset="balanced",
        parameters={"iou": iou, "confidence": confidence},
        expires_at=timezone.now()
        + timedelta(days=getattr(settings, "DETECTION_RETENTION_DAYS", 30)),
    )
    job.mark_running()
    return session, job


@transaction.atomic
def complete_camera_records(*, session, job, results, duration_ms):
    summary = summarize_camera_results(results, duration_ms=duration_ms)
    session.end_time = timezone.now()
    session.detection_count = len(results)
    session.detection_results = results[-500:]
    session.save(update_fields=["end_time", "detection_count", "detection_results"])
    job.refresh_from_db()
    if job.status == DetectionJob.Status.RUNNING:
        job.mark_succeeded(summary)
    from api.product_views import result_payload

    job.refresh_from_db()
    return result_payload(job)


@transaction.atomic
def cancel_camera_records(*, session, job):
    session.end_time = timezone.now()
    session.save(update_fields=["end_time"])
    job.refresh_from_db()
    if job.status in {
        DetectionJob.Status.QUEUED,
        DetectionJob.Status.RUNNING,
        DetectionJob.Status.CANCEL_REQUESTED,
    }:
        job.mark_cancelled()


class FrameRejected(ValueError):
    pass


@dataclass
class FramePolicy:
    max_fps: float
    max_message_bytes: int
    last_accepted_at: float | None = None

    def accept(self, *, timestamp, message_bytes):
        if message_bytes > self.max_message_bytes:
            raise FrameRejected("消息大小超过实时识别限制。")
        minimum_interval = 1 / max(float(self.max_fps), 0.1)
        if self.last_accepted_at is not None and timestamp - self.last_accepted_at < minimum_interval:
            return False
        self.last_accepted_at = timestamp
        return True


class CameraConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("sys_user")
        if not getattr(self.user, "is_authenticated", False):
            await self.close(code=4401)
            return

        self.session_id = str(self.scope["url_route"]["kwargs"].get("session_id", ""))[:64]
        query = parse_qs(self.scope.get("query_string", b"").decode("utf-8", errors="ignore"))
        try:
            self.model_id = int(query.get("modelId", [""])[0])
        except (TypeError, ValueError):
            await self.close(code=4400)
            return

        self.iou = _bounded_float(query.get("iou", ["0.5"])[0], 0.05, 0.95, 0.5)
        self.confidence = _bounded_float(
            query.get("confidence", ["0.45"])[0],
            0.05,
            0.99,
            0.45,
        )
        self.policy = FramePolicy(
            max_fps=getattr(settings, "CAMERA_MAX_FPS", 5),
            max_message_bytes=getattr(settings, "CAMERA_MAX_MESSAGE_BYTES", 2 * 1024 * 1024),
        )
        self.connected_at = time.monotonic()
        self.frame_number = 0
        self.results = []
        self.finalized = False
        self.slot_key = f"camera:user:{self.user.id}:active"
        if not await self._acquire_slot():
            await self.close(code=4429)
            return

        try:
            self.db_session, self.detection_job = await self._create_session()
        except YoloModel.DoesNotExist:
            await self._release_slot()
            await self.close(code=4404)
            return
        await self.accept()
        await self.send_json(
            {
                "type": "session.ready",
                "sessionId": self.session_id,
                "jobId": self.detection_job.id,
                "limits": {
                    "maxFps": self.policy.max_fps,
                    "maxMessageBytes": self.policy.max_message_bytes,
                    "sessionSeconds": getattr(settings, "CAMERA_SESSION_SECONDS", 300),
                },
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, "slot_key"):
            await self._release_slot()
        if hasattr(self, "db_session") and not self.finalized:
            await self._cancel_session()
            self.finalized = True

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        if text_data is None:
            await self.close(code=4400)
            return
        message_bytes = len(text_data.encode("utf-8"))
        if message_bytes > self.policy.max_message_bytes:
            await self.close(code=4409)
            return
        try:
            payload = json.loads(text_data)
        except json.JSONDecodeError:
            await self.close(code=4400)
            return
        if payload.get("type") == "frame":
            try:
                accepted = self.policy.accept(
                    timestamp=time.monotonic(),
                    message_bytes=message_bytes,
                )
            except FrameRejected:
                await self.close(code=4409)
                return
            if not accepted:
                await self.send_json({"type": "frame.skipped", "reason": "rate_limit"})
                return
        if time.monotonic() - self.connected_at > getattr(settings, "CAMERA_SESSION_SECONDS", 300):
            await self.close(code=4408)
            return
        await self.receive_json(payload)

    async def receive_json(self, content, **kwargs):
        message_type = content.get("type")
        if message_type == "session.complete":
            if not self.results:
                await self.send_json({"type": "error", "code": "NO_FRAMES_PROCESSED"})
                return
            payload = await self._complete_session()
            self.finalized = True
            await self.send_json({"type": "session.result", "result": payload})
            await self.close(code=1000)
            return
        if message_type == "session.cancel":
            await self._cancel_session()
            self.finalized = True
            await self.send_json({"type": "session.cancelled"})
            await self.close(code=1000)
            return
        if message_type != "frame" or not isinstance(content.get("image"), str):
            await self.send_json({"type": "error", "code": "INVALID_FRAME"})
            return
        encoded = content["image"].split(",", 1)[-1]
        try:
            frame = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError):
            await self.send_json({"type": "error", "code": "INVALID_FRAME"})
            return
        if len(frame) > getattr(settings, "CAMERA_MAX_FRAME_BYTES", 1_500_000):
            await self.send_json({"type": "error", "code": "FRAME_TOO_LARGE"})
            return

        self.frame_number += 1
        try:
            result = await asyncio.to_thread(self._predict_frame, frame)
            self.results.append(result)
            await self._save_detection(result)
        except Exception:
            logger.exception(
                "Camera frame inference failed",
                extra={"session_id": self.session_id, "frame_number": self.frame_number},
            )
            await self.send_json({"type": "error", "code": "INFERENCE_UNAVAILABLE"})
            return
        await self.send_json(
            {
                "type": "frame.result",
                "frame": self.frame_number,
                "result": result,
            }
        )

    def _predict_frame(self, frame):
        temporary = NamedTemporaryFile(prefix="signflow-camera-", suffix=".jpg", delete=False)
        path = Path(temporary.name)
        try:
            with temporary:
                temporary.write(frame)
            return InferenceService().predict_image(
                self.model_id,
                str(path),
                iou=self.iou,
                conf=self.confidence,
            )
        finally:
            path.unlink(missing_ok=True)

    @sync_to_async
    def _create_session(self):
        return create_camera_records(
            user=self.user,
            model_id=self.model_id,
            session_id=self.session_id,
            iou=self.iou,
            confidence=self.confidence,
        )

    @sync_to_async
    def _save_detection(self, result):
        CameraDetection.objects.create(
            session=self.db_session,
            frame_number=self.frame_number,
            detection_result=result,
        )

    @sync_to_async
    def _complete_session(self):
        duration_ms = round((time.monotonic() - self.connected_at) * 1000)
        return complete_camera_records(
            session=self.db_session,
            job=self.detection_job,
            results=self.results,
            duration_ms=duration_ms,
        )

    @sync_to_async
    def _cancel_session(self):
        cancel_camera_records(
            session=self.db_session,
            job=self.detection_job,
        )

    @sync_to_async
    def _acquire_slot(self):
        limit = getattr(settings, "CAMERA_MAX_SESSIONS_PER_USER", 2)
        cache.add(self.slot_key, 0, timeout=getattr(settings, "CAMERA_SESSION_SECONDS", 300) + 30)
        try:
            active = cache.incr(self.slot_key)
        except ValueError:
            cache.set(self.slot_key, 1, timeout=getattr(settings, "CAMERA_SESSION_SECONDS", 300) + 30)
            active = 1
        if active > limit:
            cache.decr(self.slot_key)
            return False
        return True

    @sync_to_async
    def _release_slot(self):
        try:
            active = cache.decr(self.slot_key)
            if active <= 0:
                cache.delete(self.slot_key)
        except ValueError:
            cache.delete(self.slot_key)

    async def send_json(self, content):
        await self.send(text_data=json.dumps(content, ensure_ascii=False, separators=(",", ":")))


def _bounded_float(value, minimum, maximum, default):
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return min(max(parsed, minimum), maximum)
