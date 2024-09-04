from django.core.files.storage import default_storage
from django.utils import timezone
from django.db import models
from pathlib import Path


class ActivityLog(models.Model):
    user = models.ForeignKey("accounts.account", on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.action} at {self.timestamp}"


class EmailSettings(models.Model):
    email_backend = models.CharField(
        max_length=255, default="django.core.mail.backends.smtp.EmailBackend"
    )
    email_host = models.CharField(max_length=255, default="smtp.example.com")
    email_port = models.IntegerField(db_default=587)
    email_use_tls = models.BooleanField(db_default=True)
    email_use_ssl = models.BooleanField(db_default=False)
    email_host_user = models.CharField(max_length=255)
    email_host_password = models.CharField(max_length=255)
    default_from_email = models.EmailField(db_default="info.quickdiag@gmail.com")
    email_subject_prefix = models.CharField(max_length=255, db_default="QuickDiag")
    allowed_hosts = models.TextField(default="localhost,127.0.0.1")

    def __str__(self):
        return "Email Settings"


class GeneralSettings(models.Model):
    site_name = models.CharField(max_length=255, default="MyProject")
    company = models.CharField(max_length=255, default="Zila Tech")
    tagline = models.CharField(
        max_length=255, default="Empowering Early Detection, Saving Lives"
    )
    site_description = models.TextField(blank=True, null=True)
    allow_registration = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.CharField(
        max_length=500,
        default="We are currently undergoing maintenance. We apologize for any inconvenience.",
    )
    maintenance_end_time = models.DateTimeField(blank=True, null=True)
    contact_email = models.EmailField(db_default="info.quickdiag@gmail.com")
    telephone = models.CharField(max_length=20, default="(123) 456-7890")
    address = models.CharField(
        max_length=100, default=" 123 Main Street, Paraku Estate, XEZ"
    )

    def __str__(self):
        return self.site_name


from django.db import models
import uuid


class TrainedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)  # Dynamic name for tracking
    version = models.CharField(max_length=10, default="1.0")
    model_type = models.CharField(max_length=255)

    # Performance metrics
    accuracy = models.FloatField()
    precision = models.FloatField(null=True, blank=True)
    recall = models.FloatField(null=True, blank=True)
    f1_score = models.FloatField(null=True, blank=True)

    # Metadata fields
    training_data_path = models.CharField(max_length=500)
    date_trained = models.DateTimeField(auto_now_add=True)

    # Model status flags
    is_default = models.BooleanField(default=False)

    # Path to saved model and scaler files
    model_file_path = models.CharField(max_length=500)
    scaler_file_path = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        ordering = ["-date_trained"]

    def __str__(self):
        return f"{self.name} - v{self.version} (Default: {self.is_default})"

    def set_as_default(self):
        """
        Set this model as the default model and unset others.
        """
        TrainedModel.objects.filter(is_default=True).update(is_default=False)
        self.is_default = True
        self.save()

    def save(self, *args, **kwargs):
        """
        Custom save logic: Ensures only one model is set to default at a time.
        """
        if self.is_default:
            TrainedModel.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
