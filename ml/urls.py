from django.urls import path
from .views import (
    AccountListAPIView,
    ActivityLogListView,
    AddOrUpdateUserView,
    DeleteContactsView,
    ContactDetailView,
    ContactListView,
    DashboardView,
    DataVisualizationView,
    DeactivateAccountView,
    DeleteLogView,
    FeatureExplanationView,
    GenerateReportView,
    GetUserView,
    LogDetailView,
    RecordManagementView,
    SendActivationEmailView,
    SystemSettingsView,
    TrainedModelDetailView,
    TrainedModelListView,
    UserDeleteView,
    UserManagementView,
    PredictionView,
)
from patients.views import results, summary_view

app_name = "AdminHub"

urlpatterns = [
    path("dasboard/", DashboardView.as_view(), name="dasboard"),
    path(
        "visualization/",
        DataVisualizationView.as_view(),
        name="data_visualization",
    ),
    path(
        "record-management/", RecordManagementView.as_view(), name="record_management"
    ),
    path("detailed/result/<pk>/", results, name="detailed_result"),
    path("summary/<pk>/", summary_view, name="summary"),
    path("users/", UserManagementView.as_view(), name="user-list"),
    path("add/", AddOrUpdateUserView.as_view(), name="add_user"),
    path("update/<int:user_id>/", AddOrUpdateUserView.as_view(), name="update_user"),
    path("delete-user/", UserDeleteView.as_view(), name="user_delete"),
    path("get/<int:user_id>/", GetUserView.as_view(), name="get_user"),
    path(
        "send-activation-email/",
        SendActivationEmailView.as_view(),
        name="send_activation_email",
    ),
    path(
        "deactivate-account/<int:user_id>/",
        DeactivateAccountView.as_view(),
        name="deactivate_account",
    ),
    path("contacts/", ContactListView.as_view(), name="contact_list"),
    path(
        "contact-detail/<int:pk>/", ContactDetailView.as_view(), name="contact_detail"
    ),
    path("delete-contact/", DeleteContactsView.as_view(), name="delete_contacts"),
    path("logs/", ActivityLogListView.as_view(), name="logs"),
    path("logs/details/<int:pk>/", LogDetailView.as_view(), name="log_details"),
    path("delete-log/", DeleteLogView.as_view(), name="delete_logs"),
    path("settings/", SystemSettingsView.as_view(), name="system_settings"),
    path("measurement/", PredictionView.as_view(), name="measurement"),
    path("api/users/", AccountListAPIView.as_view(), name="user-list-api"),
    path(
        "report/<prediction_id>/", GenerateReportView.as_view(), name="generate_report"
    ),
    path("feature/", FeatureExplanationView.as_view(), name="feature"),
    path("model/", TrainedModelListView.as_view(), name="model_list"),
    path(
        "model-detail/<str:pk>/", TrainedModelDetailView.as_view(), name="model_detail"
    ),
]
