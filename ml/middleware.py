from django.conf import settings
from .models import EmailSettings, GeneralSettings, TrainedModel
from django.shortcuts import render
from django.urls import resolve, reverse
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger("custom_logger")


class SettingsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            email_settings = EmailSettings.objects.first()

            if email_settings:
                logger.info("Overriding default settings with database values.")

                # Override Email Settings
                settings.EMAIL_BACKEND = email_settings.email_backend
                settings.EMAIL_HOST = email_settings.email_host
                settings.EMAIL_PORT = email_settings.email_port
                settings.EMAIL_USE_TLS = email_settings.email_use_tls
                settings.EMAIL_USE_SSL = email_settings.email_use_ssl
                settings.EMAIL_HOST_USER = email_settings.email_host_user
                settings.EMAIL_HOST_PASSWORD = email_settings.email_host_password
                settings.DEFAULT_FROM_EMAIL = email_settings.default_from_email
                settings.EMAIL_SUBJECT_PREFIX = email_settings.email_subject_prefix

                # Override ALLOWED_HOSTS if provided in the database
                if email_settings.allowed_hosts:
                    settings.ALLOWED_HOSTS = [
                        host.strip() for host in email_settings.allowed_hosts.split(",")
                    ]
                    logger.info(f"ALLOWED_HOSTS set to: {settings.ALLOWED_HOSTS}")
                else:
                    logger.info("No custom ALLOWED_HOSTS found; using .env defaults.")
            else:
                logger.info("No settings found in the database; using .env defaults.")

        except Exception as e:
            logger.error(f"Failed to load settings from the database: {e}")
            logger.info("Falling back to default .env configuration.")

        response = self.get_response(request)
        return response


class GeneralSettingsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        settings_obj = GeneralSettings.objects.first()
        request.allow_registration = (
            settings_obj.allow_registration if settings_obj else True
        )
        request.maintenance_mode = (
            settings_obj.maintenance_mode if settings_obj else False
        )

        # Handle maintenance mode
        if request.maintenance_mode:
            current_url_name = resolve(request.path_info).url_name
            app_name = resolve(request.path_info).app_name

            # Allow access to specific paths during maintenance mode
            allowed_url_names = [
                "auth:login",  # Login view
                "maintenance",  # Maintenance view itself
            ]

            # Check if the path is part of the AdminHub app
            if app_name != "AdminHub" and current_url_name not in allowed_url_names:
                context = {
                    "maintenance_message": settings_obj.maintenance_message,
                    "maintenance_end_time": settings_obj.maintenance_end_time,
                    "contact_email": settings_obj.contact_email,
                    "title_root": "Maintenance",
                }
                return render(request, "errors/maintenance.html", context)

        return None


class TrainedModelMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Try to retrieve the default trained model
        default_model = {
            "name": "model",
            "version": "0.9",
            "model_type": "RandomForestClassifier",
            "accuracy": 0.964912,
            "precision": 0.97561,
            "recall": 0.930233,
            "f1_score": 0.952381,
            "training_data_path": "/home/coder/Downloads/breastAI/static/model/data.csv",
            "model_file_path": "/home/coder/Downloads/breastAI/static/model/model.pkl",
            "scaler_file_path": "/home/coder/Downloads/breastAI/static/model/scaler.pkl",
            "date_trained": "26/08/2024",
        }
        try:
            default_model = TrainedModel.objects.filter(is_default=True).first()
        except TrainedModel.DoesNotExist:
            default_model = default_model

        # Make the default model accessible in the request object
        request.trained_model = default_model

        # Pass the request to the next middleware or view
        response = self.get_response(request)

        return response
