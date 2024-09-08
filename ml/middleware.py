from pathlib import Path
from django.conf import settings

from ml.utils import log_user_activity
from .models import EmailSettings, GeneralSettings, TrainedModel
from django.shortcuts import render, redirect
from django.urls import resolve, reverse
from django.utils.deprecation import MiddlewareMixin
import datetime
from django.contrib.auth import logout
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django.contrib import messages
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
                settings.EMAIL_HOST_USER = email_settings.email_host_user
                settings.EMAIL_HOST_PASSWORD = email_settings.email_host_password

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


class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get("last_activity")

            if last_activity is None:
                request.session["last_activity"] = now().isoformat()
            else:
                last_activity_time = datetime.datetime.fromisoformat(last_activity)
                idle_time = (now() - last_activity_time).total_seconds()

                # Check if idle time exceeds the session timeout limit
                if idle_time > settings.SESSION_COOKIE_AGE:
                    log_user_activity(
                        request, request.user, "auto logged out due to inactivity"
                    )
                    logout(request)
                    messages.info(
                        request,
                        _(
                            "You have been logged out due to inactivity. Please log in again."
                        ),
                    )
                    return redirect(settings.LOGIN_URL)

                request.session["last_activity"] = now().isoformat()

        response = self.get_response(request)
        return response


class GeneralSettingsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Default data
        default_data = {
            "site_name": "QuickDiag",
            "site_company": "Zila Tech",
            "site_telephone": "(123) 456-7890",
            "site_contact_email": "info.quickdiag@gmail.com",
            "site_address": "123 Main Street, Paraku Estate, XEZ",
            "site_tagline": "Empowering Early Detection, Saving Lives",
            "site_description": "",
            "site_allow_registration": True,
            "maintenance_mode": False,
        }

        # Fetch the first GeneralSettings object
        settings_obj = GeneralSettings.objects.first()

        # Update request attributes with settings or defaults
        request.site_name = (
            settings_obj.site_name if settings_obj else default_data["site_name"]
        )
        request.site_company = (
            settings_obj.company if settings_obj else default_data["site_company"]
        )
        request.site_tagline = (
            settings_obj.tagline if settings_obj else default_data["site_tagline"]
        )
        request.site_description = (
            settings_obj.site_description
            if settings_obj
            else default_data["site_description"]
        )
        request.allow_registration = (
            settings_obj.allow_registration
            if settings_obj
            else default_data["site_allow_registration"]
        )
        request.maintenance_mode = (
            settings_obj.maintenance_mode
            if settings_obj
            else default_data["maintenance_mode"]
        )
        request.site_telephone = (
            settings_obj.telephone if settings_obj else default_data["site_telephone"]
        )
        request.site_contact_email = (
            settings_obj.contact_email
            if settings_obj
            else default_data["site_contact_email"]
        )
        request.site_address = (
            settings_obj.address if settings_obj else default_data["site_address"]
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
                    "maintenance_message": (
                        settings_obj.maintenance_message
                        if settings_obj
                        else "The site is currently under maintenance."
                    ),
                    "maintenance_end_time": (
                        settings_obj.maintenance_end_time if settings_obj else None
                    ),
                    "contact_email": request.site_contact_email,
                    "title_root": "Maintenance",
                }
                return render(request, "errors/maintenance.html", context)

        return None


class TrainedModelMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Try to retrieve the default trained model
        model_dir = Path(f"{settings.STATICFILES_DIRS[0]}/model")
        default_model = {
            "name": "model",
            "version": "0.9",
            "model_type": "RandomForestClassifier",
            "accuracy": 0.964912,
            "precision": 0.97561,
            "recall": 0.930233,
            "f1_score": 0.952381,
            "training_data_path": model_dir / f"data.csv",
            "model_file_path": model_dir / f"model.pkl",
            "scaler_file_path": model_dir / f"scaler.pkl",
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
