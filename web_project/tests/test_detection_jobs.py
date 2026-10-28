import pytest

from modelYolo.models import YoloModel
from user.models import SysUser


@pytest.mark.django_db
def test_detection_job_moves_from_queued_to_succeeded():
    from detections.models import DetectionJob

    owner = SysUser.objects.create(username="job_owner", password="unused", status=0)
    model = YoloModel.objects.create(
        name="SignFlow Test",
        version="2.1-test",
        size="1 MB",
        status="正常",
        file_path="signflow-test.pt",
        creator=owner,
    )
    job = DetectionJob.objects.create(
        owner=owner,
        mode="image",
        asset_key="users/1/detections/input.jpg",
        model=model,
        model_snapshot={"id": model.id, "name": model.name, "version": model.version},
        preset="balanced",
        parameters={"iou": 0.5, "confidence": 0.45},
    )

    job.mark_running()
    job.mark_succeeded({"detections": [], "sentence": ""})

    assert job.status == "succeeded"
    assert job.progress == 100
    assert job.result == {"detections": [], "sentence": ""}
    assert job.started_at is not None
    assert job.completed_at is not None


@pytest.mark.django_db
def test_cancelled_job_never_accepts_a_late_result():
    from detections.models import DetectionJob

    owner = SysUser.objects.create(username="cancel_owner", password="unused", status=0)
    model = YoloModel.objects.create(
        name="SignFlow Cancel Test",
        version="2.1-test",
        size="1 MB",
        status="正常",
        file_path="signflow-test.pt",
        creator=owner,
    )
    job = DetectionJob.objects.create(
        owner=owner,
        mode="video",
        asset_key="users/1/detections/input.mp4",
        model=model,
        model_snapshot={"id": model.id, "version": model.version},
        parameters={"iou": 0.5, "confidence": 0.45},
    )
    job.mark_running()

    job.request_cancel()
    job.mark_cancelled()
    accepted = job.mark_succeeded({"detections": [{"label": "late"}]})

    job.refresh_from_db()
    assert accepted is False
    assert job.status == "cancelled"
    assert job.result is None


@pytest.mark.django_db
def test_failed_job_can_be_requeued_without_losing_its_snapshot():
    from detections.models import DetectionJob

    owner = SysUser.objects.create(username="retry_owner", password="unused", status=0)
    model = YoloModel.objects.create(
        name="SignFlow Retry Test",
        version="2.1-test",
        size="1 MB",
        status="正常",
        file_path="signflow-test.pt",
        creator=owner,
    )
    snapshot = {"id": model.id, "version": model.version}
    job = DetectionJob.objects.create(
        owner=owner,
        mode="image",
        asset_key="users/1/detections/input.jpg",
        model=model,
        model_snapshot=snapshot,
        parameters={"iou": 0.5, "confidence": 0.45},
    )
    job.mark_running()

    job.mark_failed("INFERENCE_ERROR", "模型服务暂时不可用")
    requeued = job.retry()

    assert requeued is True
    assert job.status == "queued"
    assert job.progress == 0
    assert job.attempt_count == 1
    assert job.error_code == ""
    assert job.error_message == ""
    assert job.model_snapshot == snapshot


@pytest.mark.django_db
def test_running_job_progress_is_monotonic_and_stops_below_completion():
    from detections.models import DetectionJob

    owner = SysUser.objects.create(username="progress_owner", password="unused", status=0)
    model = YoloModel.objects.create(
        name="SignFlow Progress Test",
        version="2.1-test",
        size="1 MB",
        status="正常",
        file_path="signflow-test.pt",
        creator=owner,
    )
    job = DetectionJob.objects.create(
        owner=owner,
        mode="video",
        asset_key="users/1/detections/input.mp4",
        model=model,
        model_snapshot={"id": model.id, "version": model.version},
    )
    job.mark_running()

    first_update = job.update_progress(52, "正在解析视频帧")
    stale_update = job.update_progress(31, "过期的进度消息")
    capped_update = job.update_progress(100, "等待结果落库")

    assert first_update is True
    assert stale_update is False
    assert capped_update is True
    assert job.progress == 99
    assert job.stage_label == "等待结果落库"


@pytest.mark.django_db
def test_timed_out_job_records_a_safe_reason_and_can_retry():
    from detections.models import DetectionJob

    owner = SysUser.objects.create(username="timeout_owner", password="unused", status=0)
    model = YoloModel.objects.create(
        name="SignFlow Timeout Test",
        version="2.1-test",
        size="1 MB",
        status="正常",
        file_path="signflow-test.pt",
        creator=owner,
    )
    job = DetectionJob.objects.create(
        owner=owner,
        mode="video",
        asset_key="users/1/detections/input.mp4",
        model=model,
        model_snapshot={"id": model.id, "version": model.version},
    )
    job.mark_running()

    timed_out = job.mark_timed_out("视频处理超过 10 分钟")

    assert timed_out is True
    assert job.status == "timed_out"
    assert job.error_code == "TASK_TIMEOUT"
    assert job.completed_at is not None
    assert job.retry() is True


@pytest.mark.django_db
def test_state_changes_append_an_audit_trail():
    from detections.models import DetectionJob

    owner = SysUser.objects.create(username="audit_owner", password="unused", status=0)
    model = YoloModel.objects.create(
        name="SignFlow Audit Test",
        version="2.1-test",
        size="1 MB",
        status="正常",
        file_path="signflow-test.pt",
        creator=owner,
    )
    job = DetectionJob.objects.create(
        owner=owner,
        mode="image",
        asset_key="users/1/detections/input.jpg",
        model=model,
        model_snapshot={"id": model.id, "version": model.version},
    )

    job.mark_running()
    job.update_progress(50, "正在识别")
    job.mark_succeeded({"detections": []})

    events = list(job.events.order_by("created_at").values_list("event_type", "to_status"))
    assert events == [
        ("started", "running"),
        ("progress", "running"),
        ("succeeded", "succeeded"),
    ]
