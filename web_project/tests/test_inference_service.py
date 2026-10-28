from pathlib import Path

import pytest
from PIL import Image

from modelYolo.models import YoloModel
from user.models import SysUser


class FakeBoxes:
    cls = [0.0]
    conf = [0.94]
    xyxy = [[10.0, 20.0, 110.0, 220.0]]


class FakeResult:
    names = {0: "hello"}
    boxes = FakeBoxes()


class FakeModel:
    last_source = None

    def predict(self, **kwargs):
        type(self).last_source = kwargs["source"]
        return [FakeResult()]


class FakeCslResult:
    names = {24: "thank you"}
    boxes = type(
        "FakeCslBoxes",
        (),
        {
            "cls": [24.0],
            "conf": [0.97],
            "xyxy": [[12.0, 18.0, 112.0, 218.0]],
        },
    )()


class FakeCslModel:
    def predict(self, **kwargs):
        return [FakeCslResult()]


@pytest.mark.django_db
def test_inference_service_caches_a_model_and_returns_serializable_detections(settings, tmp_path):
    from inference.service import InferenceService

    settings.MODELS_ROOT = tmp_path / "models"
    settings.MODELS_ROOT.mkdir()
    weights = settings.MODELS_ROOT / "signflow-cache.pt"
    weights.write_bytes(b"test-weights-placeholder")
    image = tmp_path / "input.jpg"
    Image.new("RGB", (8, 6), color=(20, 80, 120)).save(image)
    owner = SysUser.objects.create(username="inference_owner", password="unused", status=0)
    model = YoloModel.objects.create(
        name="SignFlow Cached Test",
        version="2.1-test",
        size="1 MB",
        status="正常",
        file_path=weights.name,
        creator=owner,
    )
    loaded_paths = []

    def loader(path):
        loaded_paths.append(Path(path))
        return FakeModel()

    InferenceService.clear_cache()
    service = InferenceService(model_loader=loader)

    first = service.predict_image(model.id, str(image), iou=0.5, conf=0.45)
    second = service.predict_image(model.id, str(image), iou=0.5, conf=0.45)

    assert loaded_paths == [weights.resolve()]
    assert first == second
    assert FakeModel.last_source.shape == (6, 8, 3)
    assert first["detections"] == [
        {
            "label": "hello",
            "classId": 0,
            "confidence": 0.94,
            "box": [10.0, 20.0, 110.0, 220.0],
        }
    ]


@pytest.mark.django_db
def test_csl_model_localizes_labels_and_preserves_the_raw_gloss(settings, tmp_path):
    from inference.service import InferenceService

    settings.MODELS_ROOT = tmp_path / "models"
    settings.MODELS_ROOT.mkdir()
    weights = settings.MODELS_ROOT / "csl.pt"
    weights.write_bytes(b"test-csl-weights-placeholder")
    image = tmp_path / "input.jpg"
    Image.new("RGB", (8, 6), color=(20, 80, 120)).save(image)
    owner = SysUser.objects.create(username="csl_inference_owner", password="unused", status=0)
    model = YoloModel.objects.create(
        name="SignFlow CSL 37",
        version="11n-local",
        size="5.3 MB",
        status="active",
        file_path=weights.name,
        creator=owner,
    )

    InferenceService.clear_cache()
    service = InferenceService(model_loader=lambda path: FakeCslModel())

    result = service.predict_image(model.id, str(image), iou=0.5, conf=0.45)

    assert result["labels"] == ["谢谢"]
    assert result["sentence"] == "谢谢"
    assert result["detections"] == [
        {
            "label": "谢谢",
            "rawLabel": "thank you",
            "classId": 24,
            "confidence": 0.97,
            "box": [12.0, 18.0, 112.0, 218.0],
        }
    ]
