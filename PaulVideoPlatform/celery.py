from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PaulVideoPlatform.settings")

app = Celery("PaulVideoPlatform")

# Using a string here means the worker doesn't need to serialize
# the configuration object to child processes.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.update(
    result_expires=3600,
)

app.conf.beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"
