import os
import secrets
from pathlib import Path
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from inference.evaluation_cards import evaluation_card_for
from modelYolo.models import YoloModel
from role.models import SysRole, SysUserRole
from user.models import SysUser


class Command(BaseCommand):
    help = "Create or update the local SignFlow product administrator."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="signflow_admin")
        parser.add_argument("--password", default="")
        parser.add_argument(
            "--credentials-file",
            default=str(Path(settings.BASE_DIR) / ".demo-credentials"),
        )

    @transaction.atomic
    def handle(self, *args, **options):
        username = options["username"].strip()
        if not username or len(username) > 100:
            raise CommandError("The administrator username must contain 1 to 100 characters.")

        supplied_password = options["password"] or os.getenv("DEMO_ADMIN_PASSWORD", "")
        password = supplied_password or secrets.token_urlsafe(18)
        if len(password) < 12:
            raise CommandError("The administrator password must contain at least 12 characters.")

        today = timezone.localdate()
        user, created = SysUser.objects.get_or_create(
            username=username,
            defaults={
                "avatar": "default.jpg",
                "status": 0,
                "create_time": today,
                "update_time": today,
            },
        )
        if created or supplied_password:
            user.set_password(password)
        user.status = 0
        user.update_time = today
        user.save()

        role = SysRole.objects.filter(code="superadmin").order_by("id").first()
        if role is None:
            role = SysRole.objects.create(
                name="超级管理员",
                code="superadmin",
                create_time=today,
                update_time=today,
                remark="SignFlow AI 产品管理员",
            )
        SysUserRole.objects.get_or_create(user=user, role=role)
        self._register_local_models(user)

        if created or supplied_password:
            credentials_path = Path(options["credentials_file"]).expanduser().resolve()
            credentials_path.parent.mkdir(parents=True, exist_ok=True)
            content = (
                "SignFlow AI local administrator account\n"
                f"username={username}\n"
                f"password={password}\n"
                "scope=local product environment only\n"
            )
            with NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=credentials_path.parent,
                delete=False,
            ) as temporary:
                temporary.write(content)
                temporary_path = Path(temporary.name)
            temporary_path.chmod(0o600)
            os.replace(temporary_path, credentials_path)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Product administrator is ready. Credentials: {credentials_path}"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Product administrator already exists; the password was not changed."
                )
            )

    def _register_local_models(self, user):
        model_root = Path(
            getattr(settings, "MODELS_ROOT", Path(settings.BASE_DIR) / "model")
        ).resolve()
        bundled_models = (
            ("SignFlow Base", "2.1-local", "ASl-v8.pt"),
            ("SignFlow CSL 37", "11n-local", "csl.pt"),
        )
        registered = False
        for name, version, filename in bundled_models:
            weights = model_root / filename
            if not weights.is_file():
                continue
            self._upsert_local_model(user, name, version, weights)
            registered = True

        if not registered:
            weights = next(iter(sorted(model_root.glob("*.pt"))), None)
            if weights is not None:
                self._upsert_local_model(user, "SignFlow Base", "2.1-local", weights)

    @staticmethod
    def _upsert_local_model(user, name, version, weights):
        size_mb = weights.stat().st_size / (1024 * 1024)
        card = evaluation_card_for(weights.name)
        model, _ = YoloModel.objects.update_or_create(
            name=name,
            defaults={
                "version": version,
                "size": f"{size_mb:.1f} MB",
                "status": "正常",
                "file_path": weights.name,
                "remark": "本地多类别手语识别模型",
                "creator": user,
                "evaluation": card,
            },
        )
        return model
