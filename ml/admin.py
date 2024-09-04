from django.contrib import admin
from django.utils import html
from ml.models import ActivityLog, EmailSettings, GeneralSettings, TrainedModel


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ["user", "action", "timestamp", "ip_address", "user_agent"]
    search_fields = ["user__email", "action", "ip_address", "user_agent"]
    list_filter = ["action", "timestamp", "ip_address"]
    list_per_page = 20
    ordering = ["-timestamp"]


@admin.register(EmailSettings)
class EmailSettingsAdmin(admin.ModelAdmin):
    list_display = [
        "email_backend",
        "email_host",
        "email_port",
        "email_use_tls",
        "email_use_ssl",
    ]
    search_fields = ["email_backend", "email_host", "email_host_user"]
    list_filter = ["email_backend", "email_use_tls", "email_use_ssl"]
    list_per_page = 10
    ordering = ["email_backend"]


@admin.register(GeneralSettings)
class GeneralSettingsAdmin(admin.ModelAdmin):
    list_display = [
        "site_name",
        "company",
        "tagline",
        "allow_registration",
        "maintenance_mode",
    ]
    search_fields = ["site_name", "company", "tagline", "contact_email"]
    list_filter = ["allow_registration", "maintenance_mode"]
    list_per_page = 10
    ordering = ["site_name"]


@admin.register(TrainedModel)
class TrainedModelAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "version",
        "model_type",
        "accuracy",
        "date_trained",
        "is_default",
    )
    list_filter = ("model_type", "is_default", "date_trained")
    search_fields = ("name", "model_type", "version")
    ordering = ("-date_trained",)
    readonly_fields = ("date_trained", "accuracy", "precision", "recall", "f1_score")
    actions = ["set_as_default"]
    list_per_page = 10
    list_editable = ("is_default",)

    def set_as_default(self, request, queryset):
        """
        Custom action to set the selected model as the default.
        """
        queryset.update(is_default=False)
        default_model = queryset.first()
        default_model.set_as_default()
        self.message_user(
            request,
            f"{default_model.name} v{default_model.version} is now the default model.",
        )

    set_as_default.short_description = "Set selected model as default"

    # Add custom coloring for the default model (optional)
    def get_list_display(self, request):
        """
        Override list display to dynamically style the rows based on the default model.
        """
        original_list_display = super().get_list_display(request)
        if "is_default" in original_list_display:
            return original_list_display + ("colored_is_default",)
        return original_list_display

    def colored_is_default(self, obj):
        """
        Display a colored tag for the default model.
        """
        color = "green" if obj.is_default else "red"
        return html.format_html(
            '<span style="color: {};">{}</span>', color, obj.is_default
        )

    colored_is_default.short_description = "Default Status"
