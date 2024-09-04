from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.forms import CustomUserChangeForm, CustomUserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import PrivacyPolicySection, PrivacyPolicySubSection, Account

admin.site.site_header = _("Breast Cancer Prediction Administration")
admin.site.site_title = _("Breast Cancer Prediction Admin Portal")
admin.site.index_title = _("Welcome to the Breast Cancer Prediction Admin Portal")


@admin.register(Account)
class AccountAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = Account
    list_display = (
        "email",
        "created_by",
        "first_name",
        "last_name",
        "username",
        "gender",
        "last_login",
        "date_joined",
        "date_of_birth",
        "is_active",
        "agree",
    )
    list_filter = (
        "email",
        "created_by",
        "first_name",
        "last_name",
        "date_of_birth",
        "gender",
        "is_staff",
        "is_active",
        "agree",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "username",
                    "gender",
                    "email",
                    "password",
                    "date_of_birth",
                    "country",
                    "agree",
                    "created_by",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_admin",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "username",
                    "gender",
                    "password1",
                    "password2",
                    "date_of_birth",
                    "country",
                    "agree",
                    "is_staff",
                    "is_active",
                    "is_admin",
                )
            },
        ),
    )
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("email",)


@admin.register(PrivacyPolicySection)
class PrivacyPolicySectionAdmin(admin.ModelAdmin):
    # List of fields to be displayed in the list view
    list_display = ["title", "order"]

    # Fields to be searched through the admin search bar
    search_fields = ["title", "content"]

    # Fields to filter by (if necessary)
    list_filter = ["order"]

    # Add pagination support (optional: this is automatic in Django but can be configured)
    list_per_page = 10

    # Ordering in the admin list view
    ordering = ["order"]


@admin.register(PrivacyPolicySubSection)
class PrivacyPolicySubSectionAdmin(admin.ModelAdmin):
    # List of fields to be displayed in the list view
    list_display = ["section", "title", "order"]

    # Fields to be searched through the admin search bar
    search_fields = ["title", "content", "section__title"]

    # Filters
    list_filter = ["section"]

    # Add pagination support
    list_per_page = 10

    # Ordering in the admin list view
    ordering = ["section", "order"]
