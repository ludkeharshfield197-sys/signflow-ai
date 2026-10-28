import hashlib

from django.core.management.base import BaseCommand, CommandError

from detections.models import DetectionJob
from storage.backends import ObjectStorage


class Command(BaseCommand):
    help = "Backfill SHA-256 evidence for retained detection media created before hash capture."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=500,
            help="Maximum number of distinct retained assets handled in this run.",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        if limit < 1 or limit > 10_000:
            raise CommandError("--limit must be between 1 and 10000.")

        keys = list(
            DetectionJob.objects.filter(input_sha256="")
            .exclude(asset_key="")
            .values_list("asset_key", flat=True)
            .distinct()[:limit]
        )
        storage = ObjectStorage()
        assets_hashed = 0
        records_updated = 0
        unavailable = 0

        for key in keys:
            if not storage.exists(key):
                unavailable += 1
                continue
            digest = hashlib.sha256()
            try:
                with storage.open(key) as source:
                    for chunk in iter(lambda: source.read(1024 * 1024), b""):
                        digest.update(chunk)
            except (FileNotFoundError, OSError):
                unavailable += 1
                continue
            records_updated += DetectionJob.objects.filter(
                asset_key=key,
                input_sha256="",
            ).update(input_sha256=digest.hexdigest())
            assets_hashed += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Backfilled "
                f"{records_updated} record(s) from {assets_hashed} asset(s); "
                f"{unavailable} asset(s) unavailable."
            )
        )
