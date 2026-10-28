from datetime import timedelta
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.utils import timezone

from detections.models import DetectionJob
from modelYolo.models import YoloModel
from user.models import SysUser


@pytest.mark.django_db
def test_retention_cleanup_is_dry_run_by_default_and_deletes_only_with_apply():
    owner = SysUser.objects.create(username="retention_owner", password="unused", status=0)
    model = YoloModel.objects.create(
        name="Retention Test",
        version="2.1-test",
        size="1 MB",
        status="正常",
        file_path="retention-test.pt",
        creator=owner,
    )
    expired = DetectionJob.objects.create(
        owner=owner,
        mode="image",
        asset_key=f"users/{owner.id}/detections/expired.jpg",
        result_asset_key=f"users/{owner.id}/detections/expired-result.jpg",
        model=model,
        model_snapshot={"id": model.id, "version": model.version},
        expires_at=timezone.now() - timedelta(days=1),
    )

    with patch(
        "detections.management.commands.purge_expired_detections.ObjectStorage.delete"
    ) as delete:
        call_command("purge_expired_detections")
        assert DetectionJob.objects.filter(pk=expired.pk).exists()
        delete.assert_not_called()

        call_command("purge_expired_detections", apply=True, limit=10)

    assert not DetectionJob.objects.filter(pk=expired.pk).exists()
    assert {call.args[0] for call in delete.call_args_list} == {
        expired.asset_key,
        expired.result_asset_key,
    }
