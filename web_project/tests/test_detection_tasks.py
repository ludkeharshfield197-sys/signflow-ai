from contextlib import contextmanager

import pytest

from modelYolo.models import YoloModel
from user.models import SysUser


class FakeObjectStorage:
    def __init__(self, local_path):
        self.local_path = local_path
        self.materialized_keys = []

    @contextmanager
    def materialize(self, key):
        self.materialized_keys.append(key)
        yield self.local_path


class FakeInferenceService:
    def predict_image(self, model_id, image_path, *, iou, conf):
        return {
            "detections": [{"label": "你好", "confidence": 0.95}],
            "labels": ["你好"],
            "sentence": "你好",
            "confidence": 0.95,
        }


@pytest.mark.django_db
def test_detection_executor_marks_a_successful_job_complete(tmp_path):
    from detections.models import DetectionJob
    from detections.tasks import execute_detection_job

    owner = SysUser.objects.create(username="task_owner", password="unused", status=0)
    model = YoloModel.objects.create(
        name="SignFlow Task Test",
        version="2.1-test",
        size="1 MB",
        status="正常",
        file_path="signflow-test.pt",
        creator=owner,
    )
    job = DetectionJob.objects.create(
        owner=owner,
        mode="image",
        asset_key=f"users/{owner.id}/detections/input.jpg",
        model=model,
        model_snapshot={"id": model.id, "version": model.version},
        parameters={"iou": 0.5, "confidence": 0.45},
    )
    local_path = tmp_path / "input.jpg"
    local_path.write_bytes(b"materialized-test-image")
    storage = FakeObjectStorage(local_path)

    outcome = execute_detection_job(
        job.id,
        inference_service=FakeInferenceService(),
        object_storage=storage,
    )

    job.refresh_from_db()
    assert outcome == "succeeded"
    assert storage.materialized_keys == [job.asset_key]
    assert job.status == "succeeded"
    assert job.progress == 100
    assert job.result["sentence"] == "你好"


@pytest.mark.django_db
def test_detection_executor_discards_a_result_after_cancellation(tmp_path):
    from detections.models import DetectionJob
    from detections.tasks import execute_detection_job

    owner = SysUser.objects.create(username="cancel_task_owner", password="unused", status=0)
    model = YoloModel.objects.create(
        name="SignFlow Cancel Task Test",
        version="2.1-test",
        size="1 MB",
        status="正常",
        file_path="signflow-test.pt",
        creator=owner,
    )
    job = DetectionJob.objects.create(
        owner=owner,
        mode="image",
        asset_key=f"users/{owner.id}/detections/input.jpg",
        model=model,
        model_snapshot={"id": model.id, "version": model.version},
    )
    local_path = tmp_path / "input.jpg"
    local_path.write_bytes(b"materialized-test-image")

    class CancellingService:
        def predict_image(self, model_id, image_path, *, iou, conf):
            current = DetectionJob.objects.get(pk=job.id)
            current.request_cancel()
            return {"sentence": "不应写入", "detections": [{"label": "late"}]}

    outcome = execute_detection_job(
        job.id,
        inference_service=CancellingService(),
        object_storage=FakeObjectStorage(local_path),
    )

    job.refresh_from_db()
    assert outcome == "cancelled"
    assert job.status == "cancelled"
    assert job.result is None


@pytest.mark.django_db
def test_queue_failure_moves_the_job_to_a_visible_failed_state(monkeypatch):
    from detections.models import DetectionJob
    from detections.tasks import enqueue_detection_job, process_detection_job

    owner = SysUser.objects.create(username="queue_failure_owner", password="unused", status=0)
    model = YoloModel.objects.create(
        name="SignFlow Queue Failure Test",
        version="2.1-test",
        size="1 MB",
        status="正常",
        file_path="signflow-test.pt",
        creator=owner,
    )
    job = DetectionJob.objects.create(
        owner=owner,
        mode="image",
        asset_key=f"users/{owner.id}/detections/input.jpg",
        model=model,
        model_snapshot={"id": model.id, "version": model.version},
    )

    def unavailable_broker(**kwargs):
        raise ConnectionError("test broker unavailable")

    monkeypatch.setattr(process_detection_job, "apply_async", unavailable_broker)

    task_id = enqueue_detection_job(job.id)

    job.refresh_from_db()
    assert task_id is None
    assert job.status == "failed"
    assert job.error_code == "QUEUE_UNAVAILABLE"


@pytest.mark.django_db
def test_eager_mode_executes_locally_without_relabeling_inference_failures(
    monkeypatch,
    settings,
):
    from detections.models import DetectionJob
    from detections.tasks import enqueue_detection_job

    owner = SysUser.objects.create(username="eager_owner", password="unused", status=0)
    model = YoloModel.objects.create(
        name="SignFlow Eager Test",
        version="2.1-test",
        size="1 MB",
        status="正常",
        file_path="signflow-test.pt",
        creator=owner,
    )
    job = DetectionJob.objects.create(
        owner=owner,
        mode="image",
        asset_key=f"users/{owner.id}/detections/input.jpg",
        model=model,
        model_snapshot={"id": model.id, "version": model.version},
    )
    settings.CELERY_TASK_ALWAYS_EAGER = True

    monkeypatch.setattr(
        "detections.tasks.execute_detection_job",
        lambda job_id: "failed",
    )

    task_id = enqueue_detection_job(job.id)

    job.refresh_from_db()
    assert task_id == f"eager:{job.id}"
    assert job.error_code != "QUEUE_UNAVAILABLE"
