import pytest
from rest_framework.test import APIClient

from user.models import SysUser


def test_camera_frame_policy_enforces_message_size_and_frame_rate():
    from CameraModel.consumers import FramePolicy, FrameRejected

    policy = FramePolicy(max_fps=5, max_message_bytes=1024)

    assert policy.accept(timestamp=10.0, message_bytes=512) is True
    assert policy.accept(timestamp=10.05, message_bytes=512) is False
    assert policy.accept(timestamp=10.21, message_bytes=512) is True
    with pytest.raises(FrameRejected, match="消息大小"):
        policy.accept(timestamp=10.5, message_bytes=2048)


def test_camera_session_summary_collapses_adjacent_labels_and_keeps_trace_data():
    from CameraModel.consumers import summarize_camera_results

    result = summarize_camera_results(
        [
            {
                "labels": ["你"],
                "confidence": 0.92,
                "detections": [{"label": "你", "confidence": 0.92}],
            },
            {
                "labels": ["你", "好"],
                "confidence": 0.96,
                "detections": [{"label": "好", "confidence": 0.96}],
            },
        ],
        duration_ms=1200,
    )

    assert result["sentence"] == "你 好"
    assert result["labels"] == ["你", "好"]
    assert result["confidence"] == 0.94
    assert result["frames"] == 2
    assert result["durationMs"] == 1200
    assert len(result["detections"]) == 2


@pytest.mark.django_db
def test_camera_session_is_persisted_as_an_owned_detection_result():
    from CameraModel.consumers import complete_camera_records, create_camera_records
    from detections.models import DetectionJob
    from modelYolo.models import YoloModel

    owner = SysUser.objects.create(username="camera_result_owner", password="unused", status=0)
    model = YoloModel.objects.create(
        name="SignFlow Camera Test",
        version="2.1-test",
        size="1 MB",
        status="正常",
        file_path="camera-test.pt",
        creator=owner,
    )

    session, job = create_camera_records(
        user=owner,
        model_id=model.id,
        session_id="camera-owned-result",
        iou=0.5,
        confidence=0.45,
    )
    assert job.status == DetectionJob.Status.RUNNING

    payload = complete_camera_records(
        session=session,
        job=job,
        results=[{"labels": ["你好"], "confidence": 0.95, "detections": []}],
        duration_ms=900,
    )

    job.refresh_from_db()
    session.refresh_from_db()
    assert job.status == DetectionJob.Status.SUCCEEDED
    assert job.result["sentence"] == "你好"
    assert session.end_time is not None
    assert payload["id"] == job.id
    assert payload["mode"] == "live"
    assert payload["dataKind"] == "real"


@pytest.mark.django_db
def test_camera_ticket_is_short_lived_and_single_use():
    from api.channels import consume_camera_ticket

    user = SysUser.objects.create(username="camera_owner", password="unused", status=0)
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post("/api/v1/camera/tickets/", {}, format="json")

    assert response.status_code == 201
    assert response.data["data"]["expiresIn"] == 60
    ticket = response.data["data"]["ticket"]
    assert consume_camera_ticket(ticket).id == user.id
    assert consume_camera_ticket(ticket) is None


@pytest.mark.django_db
def test_camera_ticket_accepts_legacy_active_users_with_null_status():
    from api.channels import consume_camera_ticket, issue_camera_ticket

    user = SysUser.objects.create(username="legacy_camera_owner", password="unused", status=None)

    authenticated = consume_camera_ticket(issue_camera_ticket(user))

    assert authenticated.id == user.id
