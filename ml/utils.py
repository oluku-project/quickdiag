import json
from django.shortcuts import get_object_or_404
from accounts.models import Account
from ml.models import ActivityLog
from decimal import Decimal


def log_user_activity(request,user, action):
    if isinstance(user,Account):
        ActivityLog.objects.create(
            user=user,
            action=action,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT"),
        )


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder for Decimal objects."""

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)
