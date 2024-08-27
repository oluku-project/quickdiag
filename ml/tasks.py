from celery import shared_task
from django.utils import timezone
from .models import ActivityLog
import datetime


@shared_task
def delete_old_logs():
    retention_period = timezone.now() - datetime.timedelta(days=90)
    ActivityLog.objects.filter(timestamp__lt=retention_period).delete()
