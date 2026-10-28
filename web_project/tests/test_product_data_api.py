import pytest
from rest_framework.test import APIClient

from modelYolo.models import YoloModel
from user.models import SysUser


@pytest.mark.django_db
def test_results_api_returns_only_the_owners_commercial_result_shape():
    from detections.models import DetectionJob

    owner = SysUser.objects.create(username="results_owner", password="unused", status=0)
    other = SysUser.objects.create(username="results_other", password="unused", status=0)
    model = YoloModel.objects.create(
        name="SignFlow Results Test",
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
        original_filename="gesture.jpg",
        model=model,
        model_snapshot={
            "id": model.id,
            "name": model.name,
            "version": model.version,
            "fileSize": model.size,
        },
        preset="balanced",
        parameters={"iou": 0.5, "confidence": 0.45},
    )
    job.mark_running()
    job.mark_succeeded(
        {
            "sentence": "你好",
            "confidence": 0.95,
            "labels": [{"text": "你好", "confidence": 0.95, "startMs": 0, "endMs": 1000}],
            "inputDurationMs": 1000,
            "frames": 1,
        }
    )
    DetectionJob.objects.create(
        owner=other,
        mode="image",
        asset_key=f"users/{other.id}/detections/private.jpg",
        model=model,
        model_snapshot={"id": model.id, "version": model.version},
    )
    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.get("/api/v1/results/?page=1&pageSize=10")

    assert response.status_code == 200
    assert response.data["data"]["total"] == 1
    item = response.data["data"]["items"][0]
    assert item["id"] == job.id
    assert item["sentence"] == "你好"
    assert item["model"]["version"] == "2.1-test"
    assert item["advanced"] == {"iou": 0.5, "confidence": 0.45}
    assert item["dataKind"] == "real"
    assert "asset_key" not in item


@pytest.mark.django_db
def test_result_without_detections_does_not_invent_zero_confidence():
    from detections.models import DetectionJob

    owner = SysUser.objects.create(username="empty_result_owner", password="unused", status=0)
    model = YoloModel.objects.create(
        name="SignFlow Empty Result Test",
        version="2.1-test",
        size="1 MB",
        status="正常",
        file_path="signflow-test.pt",
        creator=owner,
    )
    job = DetectionJob.objects.create(
        owner=owner,
        mode="video",
        asset_key=f"users/{owner.id}/detections/empty.mp4",
        model=model,
        model_snapshot={"id": model.id, "name": model.name, "version": model.version},
    )
    job.mark_running()
    job.mark_succeeded({"sentence": "", "confidence": None, "labels": []})
    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.get(f"/api/v1/results/{job.id}/")

    assert response.status_code == 200
    assert response.data["data"]["confidence"] is None
    assert response.data["data"]["labels"] == []


@pytest.mark.django_db
def test_model_catalog_exposes_governance_metadata_without_invented_metrics():
    owner = SysUser.objects.create(username="models_owner", password="unused", status=0)
    model = YoloModel.objects.create(
        name="SignFlow Catalog Test",
        version="2.1-test",
        size="42 MB",
        status="正常",
        file_path="ASl-v8.pt",
        remark="本地多类别手语识别模型",
        creator=owner,
        evaluation={
            "status": "evaluated",
            "dataset": {
                "name": "ASL-80 带框保留验证集",
                "split": "validation",
                "sampleCount": 2053,
                "instanceCount": 2085,
                "independence": "训练期间使用的验证集，不等同于独立测试集",
            },
            "metrics": {
                "precision": 0.976252,
                "recall": 0.988073,
                "map50": 0.989351,
                "map5095": 0.76944,
            },
            "performance": {
                "averageImageLatencyMs": 83.15,
                "videoFps": 11.75,
                "hardware": "Intel Core i7-13700H CPU",
                "imageSize": 640,
            },
            "regressionSet": {
                "name": "SignFlow 独立产品回归集",
                "sampleCount": 10,
                "precision": 1.0,
                "recall": 1.0,
            },
            "evaluatedAt": "2026-07-30",
            "limitations": ["ASL 检测指标来自训练期保留验证集，不能替代外部盲测。"],
        },
    )
    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.get("/api/v1/models/")

    assert response.status_code == 200
    item = response.data["data"]["items"][0]
    assert item["id"] == model.id
    assert item["version"] == "2.1-test"
    assert item["fileSize"] == "42 MB"
    assert item["metric"]["value"] == "98.9%"
    assert item["metric"]["source"] == "本地 YOLO.val 复测"
    assert item["metric"]["sampleCount"] == 2053
    assert item["evaluation"]["metrics"]["precision"] == 0.976252
    assert item["evaluation"]["performance"]["videoFps"] == 11.75
    assert item["evaluation"]["limitations"]
    assert item["description"] == "本地多类别手语识别模型"
    assert "file_path" not in item


@pytest.mark.django_db
def test_model_catalog_describes_the_local_chinese_sign_language_model():
    owner = SysUser.objects.create(username="csl_catalog_owner", password="unused", status=0)
    model = YoloModel.objects.create(
        name="SignFlow CSL 37",
        version="11n-local",
        size="5.3 MB",
        status="active",
        file_path="csl.pt",
        remark="37 类中国手语本地识别模型",
        creator=owner,
    )
    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.get("/api/v1/models/")

    assert response.status_code == 200
    item = next(entry for entry in response.data["data"]["items"] if entry["id"] == model.id)
    assert item["classes"] == 37
    assert item["language"] == "中国手语（CSL）"
    assert item["languageCode"] == "csl"


@pytest.mark.django_db
def test_overview_uses_real_owned_jobs_for_metrics_and_recent_results():
    from detections.models import DetectionJob

    owner = SysUser.objects.create(username="overview_owner", password="unused", status=0)
    model = YoloModel.objects.create(
        name="SignFlow Overview Test",
        version="2.1-test",
        size="1 MB",
        status="正常",
        file_path="signflow-test.pt",
        creator=owner,
    )
    completed = DetectionJob.objects.create(
        owner=owner,
        mode="image",
        asset_key=f"users/{owner.id}/detections/completed.jpg",
        original_filename="completed.jpg",
        model=model,
        model_snapshot={"id": model.id, "name": model.name, "version": model.version},
    )
    completed.mark_running()
    completed.mark_succeeded({"sentence": "你好", "confidence": 0.93, "labels": []})
    DetectionJob.objects.create(
        owner=owner,
        mode="video",
        asset_key=f"users/{owner.id}/detections/queued.mp4",
        original_filename="queued.mp4",
        model=model,
        model_snapshot={"id": model.id, "name": model.name, "version": model.version},
    )
    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.get("/api/v1/overview/")

    assert response.status_code == 200
    assert response.data["data"]["metrics"]["completed"] == 1
    assert response.data["data"]["metrics"]["pending"] == 1
    assert response.data["data"]["metrics"]["successRate"] == 100
    assert response.data["data"]["recentResults"][0]["id"] == completed.id
    assert response.data["data"]["source"] == "SignFlow AI 实际识别任务"


@pytest.mark.django_db
def test_analytics_aggregates_real_jobs_by_day_mode_and_terminal_status():
    from detections.models import DetectionJob

    owner = SysUser.objects.create(username="analytics_owner", password="unused", status=0)
    model = YoloModel.objects.create(
        name="SignFlow Analytics Test",
        version="2.1-test",
        size="1 MB",
        status="正常",
        file_path="signflow-test.pt",
        creator=owner,
    )
    succeeded = DetectionJob.objects.create(
        owner=owner,
        mode="image",
        asset_key=f"users/{owner.id}/detections/succeeded.jpg",
        model=model,
        model_snapshot={"id": model.id, "version": model.version},
    )
    succeeded.mark_running()
    succeeded.mark_succeeded({"sentence": "你好", "confidence": 0.94, "labels": ["你", "好"]})
    failed = DetectionJob.objects.create(
        owner=owner,
        mode="video",
        asset_key=f"users/{owner.id}/detections/failed.mp4",
        model=model,
        model_snapshot={"id": model.id, "version": model.version},
    )
    failed.mark_running()
    failed.mark_failed("INFERENCE_ERROR", "识别失败")
    DetectionJob.objects.create(
        owner=owner,
        mode="image",
        asset_key=f"users/{owner.id}/detections/queued.jpg",
        model=model,
        model_snapshot={"id": model.id, "version": model.version},
    )
    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.get("/api/v1/analytics/?range=7d")

    assert response.status_code == 200
    payload = response.data["data"]
    assert payload["range"] == "最近 7 天"
    assert payload["metrics"] == {
        "tasks": 3,
        "successRate": 50,
        "averageLatencyMs": payload["daily"][-1]["latencyMs"],
    }
    assert payload["daily"][-1]["tasks"] == 3
    assert payload["daily"][-1]["successRate"] == 50
    assert payload["modes"] == [
        {"name": "图片", "value": 2},
        {"name": "视频", "value": 1},
    ]
    assert payload["popularLabels"][0] == {"name": "你", "value": 1}
    assert payload["source"] == "SignFlow AI 实际识别任务"
