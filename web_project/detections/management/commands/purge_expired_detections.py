from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils import timezone

from detections.models import DetectionJob
from storage.backends import ObjectStorage


class Command(BaseCommand):
    help = "Preview or remove expired detection jobs and their stored media."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Perform the deletion. Without this option the command is a dry run.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=500,
            help="Maximum number of expired jobs handled in this run.",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        if limit < 1 or limit > 10_000:
            raise CommandError("--limit must be between 1 and 10000.")

        jobs = list(
            DetectionJob.objects.filter(expires_at__lte=timezone.now())
            .order_by("expires_at")
            .only("id", "asset_key", "result_asset_key")[:limit]
        )
        if not options["apply"]:
            self.stdout.write(
                self.style.WARNING(
                    f"Dry run: {len(jobs)} expired detection job(s) would be removed."
                )
            )
            return

        storage = ObjectStorage()
        deleted = 0
        for job in jobs:
            for key in (job.asset_key, job.result_asset_key):
                if not key:
                    continue
                shared = (
                    DetectionJob.objects.exclude(pk=job.pk)
                    .filter(Q(asset_key=key) | Q(result_asset_key=key))
                    .exists()
                )
                if not shared:
                    storage.delete(key)
            job.delete()
            deleted += 1
        self.stdout.write(self.style.SUCCESS(f"Removed {deleted} expired detection job(s)."))
