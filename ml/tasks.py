from celery import shared_task
from django.utils import timezone

from patients.utils import HelpResponse
from .models import ActivityLog
import datetime
from time import sleep
from ml.management.commands.train_model import Command as TrainCommand


@shared_task
def delete_old_logs():
    retention_period = timezone.now() - datetime.timedelta(days=90)
    ActivityLog.objects.filter(timestamp__lt=retention_period).delete()


@shared_task(bind=True)
def train_model_task(self, model_type):
    """
    Celery task to train the model asynchronously with progress updates.
    """
    try:
        total_steps = 5  # Customize this based on the number of stages in training

        # Step 1: Load Data
        self.update_state(
            state="PROGRESS",
            meta={"current": 1, "total": total_steps, "status": "Loading data..."},
        )
        sleep(1)  # Simulate some delay for this step (for demo purposes)

        # Step 2: Train model
        self.update_state(
            state="PROGRESS",
            meta={"current": 2, "total": total_steps, "status": "Training model..."},
        )
        train_command = TrainCommand()
        train_command.handle(model_type=model_type)

        # Step 3: Validate model
        self.update_state(
            state="PROGRESS",
            meta={"current": 3, "total": total_steps, "status": "Validating model..."},
        )
        sleep(1)  # Simulate model validation

        # Step 4: Save model
        self.update_state(
            state="PROGRESS",
            meta={"current": 4, "total": total_steps, "status": "Saving model..."},
        )
        sleep(1)  # Simulate model saving

        # Step 5: Completion
        self.update_state(
            state="PROGRESS",
            meta={"current": 5, "total": total_steps, "status": "Finalizing..."},
        )
        sleep(1)

        # Task completion
        return {
            "status": "success",
            "message": f"Model {model_type} trained successfully.",
        }

    except Exception as e:
        self.update_state(
            state="FAILURE", meta={"current": 0, "total": total_steps, "status": str(e)}
        )
        raise


"""
python manage.py collectstatic --no-post-process

sudo service redis-server start
sudo systemctl status redis


celery -A PaulVideoPlatform worker --loglevel=info

gunicorn --workers 3 --bind 127.0.0.1:8000 PaulVideoPlatform.wsgi:application  OR

gunicorn -c gunicorn_config.py PaulVideoPlatform.wsgi:application

python manage.py runserver --insecure

"""
