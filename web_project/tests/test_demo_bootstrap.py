import pytest
from django.core.management import call_command

from modelYolo.models import YoloModel
from role.models import SysUserRole
from user.models import SysUser


@pytest.mark.django_db
def test_demo_bootstrap_creates_a_hashed_superadmin_without_plaintext_storage(tmp_path):
    credentials_file = tmp_path / "credentials.txt"

    call_command(
        "bootstrap_demo",
        username="signflow_admin",
        password="Local-Product-Admin-Password-2026!",
        credentials_file=str(credentials_file),
    )

    user = SysUser.objects.get(username="signflow_admin")
    assert user.password != "Local-Product-Admin-Password-2026!"
    assert user.check_password("Local-Product-Admin-Password-2026!", upgrade_legacy=False)
    assert SysUserRole.objects.filter(user=user, role__code="superadmin").exists()
    assert "signflow_admin" in credentials_file.read_text(encoding="utf-8")
    assert "Local-Product-Admin-Password-2026!" in credentials_file.read_text(encoding="utf-8")


@pytest.mark.django_db
def test_bootstrap_uses_product_neutral_credentials_and_model_description(settings, tmp_path):
    model_root = tmp_path / "models"
    model_root.mkdir()
    (model_root / "ASL-v8.pt").write_bytes(b"local-model-placeholder")
    settings.MODELS_ROOT = model_root
    credentials_file = tmp_path / "credentials.txt"

    call_command(
        "bootstrap_demo",
        username="signflow_product_admin",
        password="Local-Product-Admin-Password-2026!",
        credentials_file=str(credentials_file),
    )

    credentials = credentials_file.read_text(encoding="utf-8")
    model = YoloModel.objects.get(name="SignFlow Base")
    forbidden = ("比赛", "竞赛", "参赛", "competition", "demonstration")
    assert model.remark == "本地多类别手语识别模型"
    assert not any(word in credentials.lower() for word in forbidden)


@pytest.mark.django_db
def test_bootstrap_registers_bundled_asl_and_csl_models(settings, tmp_path):
    model_root = tmp_path / "models"
    model_root.mkdir()
    (model_root / "ASl-v8.pt").write_bytes(b"asl-model-placeholder")
    (model_root / "csl.pt").write_bytes(b"csl-model-placeholder")
    settings.MODELS_ROOT = model_root

    call_command(
        "bootstrap_demo",
        username="signflow_product_admin",
        password="Local-Product-Admin-Password-2026!",
        credentials_file=str(tmp_path / "credentials.txt"),
    )

    assert set(YoloModel.objects.values_list("file_path", flat=True)) == {
        "ASl-v8.pt",
        "csl.pt",
    }
