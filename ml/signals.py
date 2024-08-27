from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import TrainedModel
import os


@receiver(post_delete, sender=TrainedModel)
def delete_files_on_model_delete(sender, instance, **kwargs):
    if os.path.exists(instance.model_file_path):
        os.remove(instance.model_file_path)
    if instance.scaler_file_path and os.path.exists(instance.scaler_file_path):
        os.remove(instance.scaler_file_path)
