import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_project.settings.dev")

app = Celery("signflow")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
