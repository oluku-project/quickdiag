from django.contrib import admin

from patients.models import *

from django.urls import reverse
from django.utils.html import format_html


@admin.register(QuestionnaireResponse)
class QuestionnaireResponseAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "created_by",
        "progress",
        "submission_date",
        "updated_date",
        "state",
        "score",
        "result_display",
    ]
    search_fields = ["user__username", "created_by__username", "state"]
    list_filter = ["state", "submission_date", "progress"]
    list_per_page = 15
    ordering = ["-submission_date"]

    def score(self, obj):
        return obj.score

    score.admin_order_field = "score"
    score.short_description = "Score"

    def result_display(self, obj):
        result = obj.result
        if result:
            url = reverse("admin:prediction_predictionresult_change", args=[result.id])
            return format_html('<a href="{}">View Result</a>', url)
        return "No result"

    result_display.admin_order_field = "result"
    result_display.short_description = "Result"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("user", "created_by")


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ["questionnaire_response", "question_key"]
    search_fields = ["question_key", "questionnaire_response__user__username"]
    list_filter = ["questionnaire_response"]
    list_per_page = 20
    ordering = ["questionnaire_response", "question_key"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("questionnaire_response")


class PredictionResultAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "risk_level",
        "risk_score",
        "probability_benign",
        "probability_malignant",
        "submission_date",
        "dob",
        "deleted",
    )
    list_per_page = 10
    list_filter = ("deleted",)
    actions = ["delete_selected", "restore_selected"]

    def get_queryset(self, request):
        # Override the queryset to include deleted objects for superusers and staff
        return PredictionResult.objects.for_user(request.user)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser and not request.user.is_staff:
            if "delete_selected" in actions:
                del actions["delete_selected"]
        return actions

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff

    def delete_selected(self, request, queryset):
        # Custom delete action to set deleted=True instead of actual deletion
        queryset.update(deleted=True)

    delete_selected.short_description = "Mark selected as deleted"

    def restore_selected(self, request, queryset):
        # Custom action to restore deleted objects
        queryset.update(deleted=False)

    restore_selected.short_description = "Restore selected deleted objects"


admin.site.register(PredictionResult, PredictionResultAdmin)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("get_user", "rating", "show", "submitted_at", "view_result_link")
    list_filter = ("rating", "show", "submitted_at")
    search_fields = ("result__user__username", "rating", "message")
    list_editable = ("show",)
    list_per_page = 10
    ordering = ("-submitted_at",)
    readonly_fields = ("submitted_at",)

    def get_user(self, obj):
        return obj.result.user.username

    get_user.short_description = "User"

    def view_result_link(self, obj):
        if obj.result:
            url = f"/admin/patients/predictionresult/{obj.result.id}/change/"
            return format_html('<a href="{}">View Prediction</a>', url)
        return "No Result"

    view_result_link.short_description = "Prediction Result"

    def save_model(self, request, obj, form, change):
        if obj.show:
            count = Feedback.objects.filter(show=True).count()
            if count >= 3 and not obj.pk:
                self.message_user(
                    request,
                    "Cannot have more than 3 feedback items marked to show.",
                    level="error",
                )
                obj.show = False
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        # Custom logic to prevent deletion based on condition
        return super().has_delete_permission(request, obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("result__user")


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "submitted_at")
    search_fields = ("name", "email", "message")
    list_per_page = 10
