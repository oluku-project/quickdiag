import datetime
import django_filters
from django import forms

from ml.models import ActivityLog, TrainedModel
from patients.utils import RATE_CHOICES
from .models import STATE, Contact, Feedback, PredictionResult
from django.db.models import F, ExpressionWrapper, DurationField, IntegerField
from django.db.models.functions import Now


class DateInput(forms.DateInput):
    input_type = "date"


class PredictionResultFilter(django_filters.FilterSet):
    # User field
    user = django_filters.CharFilter(
        field_name="user__username",
        lookup_expr="icontains",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by Username"}
        ),
    )

    # Risk Level field
    risk_level = django_filters.CharFilter(
        field_name="risk_level",
        lookup_expr="icontains",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by Risk Level"}
        ),
    )

    # Risk Score Min field
    risk_score_min = django_filters.NumberFilter(
        field_name="risk_score",
        lookup_expr="gte",
        label="Min Risk Score",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Min Risk Score"}
        ),
    )

    # Risk Score Max field
    risk_score_max = django_filters.NumberFilter(
        field_name="risk_score",
        lookup_expr="lte",
        label="Max Risk Score",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Max Risk Score"}
        ),
    )

    # Probability Benign Min field
    probability_benign_min = django_filters.NumberFilter(
        field_name="probability_benign",
        lookup_expr="gte",
        label="Min Probability Benign",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Min Probability Benign"}
        ),
    )

    # Probability Benign Max field
    probability_benign_max = django_filters.NumberFilter(
        field_name="probability_benign",
        lookup_expr="lte",
        label="Max Probability Benign",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Max Probability Benign"}
        ),
    )

    # Probability Malignant Min field
    probability_malignant_min = django_filters.NumberFilter(
        field_name="probability_malignant",
        lookup_expr="gte",
        label="Min Probability Malignant",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Min Probability Malignant"}
        ),
    )

    # Probability Malignant Max field
    probability_malignant_max = django_filters.NumberFilter(
        field_name="probability_malignant",
        lookup_expr="lte",
        label="Max Probability Malignant",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Max Probability Malignant"}
        ),
    )

    # Submission Date Start field
    submission_date_start = django_filters.DateFilter(
        field_name="submission_date",
        lookup_expr="gte",
        label="Submission Date Start",
        widget=DateInput(
            attrs={"class": "form-control", "placeholder": "Submission Date Start"}
        ),
    )

    # Submission Date End field
    submission_date_end = django_filters.DateFilter(
        field_name="submission_date",
        lookup_expr="lte",
        label="Submission Date End",
        widget=DateInput(
            attrs={"class": "form-control", "placeholder": "Submission Date End"}
        ),
    )

    # Date of Birth Start field
    dob_start = django_filters.DateFilter(
        field_name="dob",
        lookup_expr="gte",
        label="Date of Birth Start",
        widget=DateInput(
            attrs={"class": "form-control", "placeholder": "Date of Birth Start"}
        ),
    )

    # Date of Birth End field
    dob_end = django_filters.DateFilter(
        field_name="dob",
        lookup_expr="lte",
        label="Date of Birth End",
        widget=DateInput(
            attrs={"class": "form-control", "placeholder": "Date of Birth End"}
        ),
    )

    # Age Min field
    min_age = django_filters.NumberFilter(
        method="filter_min_age",
        label="Min Age",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Min Age"}
        ),
    )

    # Age Max field
    max_age = django_filters.NumberFilter(
        method="filter_max_age",
        label="Max Age",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Max Age"}
        ),
    )

    def filter_min_age(self, queryset, name, value):
        now = datetime.datetime.now()
        min_dob = now - datetime.timedelta(days=int(value) * 365.25)
        return queryset.filter(dob__lte=min_dob)

    def filter_max_age(self, queryset, name, value):
        now = datetime.datetime.now()
        max_dob = now - datetime.timedelta(days=int(value) * 365.25)
        return queryset.filter(dob__gte=max_dob)

    class Meta:
        model = PredictionResult
        fields = [
            "user",
            "risk_level",
            "risk_score_min",
            "risk_score_max",
            "probability_benign_min",
            "probability_benign_max",
            "probability_malignant_min",
            "probability_malignant_max",
            "submission_date_start",
            "submission_date_end",
            "dob_start",
            "dob_end",
            "min_age",
            "max_age",
        ]


class QuestionnaireResponseFilter(django_filters.FilterSet):
    # Progress Min field
    progress_min = django_filters.NumberFilter(
        field_name="progress",
        lookup_expr="gte",
        label="Min Progress Score",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Min Progress Score"}
        ),
    )

    # Progress Score Max field
    progress_max = django_filters.NumberFilter(
        field_name="progress",
        lookup_expr="lte",
        label="Max Progress Score",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Max Progress Score"}
        ),
    )

    # Submission Date Start field
    submission_date_start = django_filters.DateFilter(
        field_name="submission_date",
        lookup_expr="gte",
        label="Submission Date Start",
        widget=DateInput(
            attrs={"class": "form-control", "placeholder": "Submission Date Start"}
        ),
    )

    # Submission Date End field
    submission_date_end = django_filters.DateFilter(
        field_name="submission_date",
        lookup_expr="lte",
        label="Submission Date End",
        widget=DateInput(
            attrs={"class": "form-control", "placeholder": "Submission Date End"}
        ),
    )
    # Updated Date Start field
    updated_date_start = django_filters.DateFilter(
        field_name="updated_date",
        lookup_expr="gte",
        label="Updated Date Start",
        widget=DateInput(
            attrs={"class": "form-control", "placeholder": "Updated Date Start"}
        ),
    )

    # Updated Date End field
    updated_date_end = django_filters.DateFilter(
        field_name="updated_date",
        lookup_expr="lte",
        label="Updated Date End",
        widget=DateInput(
            attrs={"class": "form-control", "placeholder": "Updated Date End"}
        ),
    )
    state = django_filters.ChoiceFilter(
        field_name="state",
        label="State",
        choices=STATE.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = PredictionResult
        fields = [
            "progress_min",
            "progress_max",
            "submission_date_start",
            "submission_date_end",
            "updated_date_start",
            "updated_date_end",
            "state",
        ]


class ContactFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(
        field_name="user__username",
        lookup_expr="icontains",
        label="User",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by Username"}
        ),
    )
    name = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Name",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by Name"}
        ),
    )
    subject = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Subject",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by Subject"}
        ),
    )
    email = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Email",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Search by Email"}
        ),
    )
    # Submission Date Start field
    submission_date_start = django_filters.DateFilter(
        field_name="submission_date",
        lookup_expr="gte",
        label="Submission Date Start",
        widget=DateInput(
            attrs={"class": "form-control", "placeholder": "Submission Date Start"}
        ),
    )

    # Submission Date End field
    submission_date_end = django_filters.DateFilter(
        field_name="submission_date",
        lookup_expr="lte",
        label="Submission Date End",
        widget=DateInput(
            attrs={"class": "form-control", "placeholder": "Submission Date End"}
        ),
    )

    class Meta:
        model = Contact
        fields = [
            "user",
            "name",
            "subject",
            "email",
            "submission_date_start",
            "submission_date_end",
        ]


class TrainedModelFilterFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Name",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by Name"}
        ),
    )
    version = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Version",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by Version"}
        ),
    )
    model_type = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Model Type",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by Model Type"}
        ),
    )
    accuracy_min = django_filters.NumberFilter(
        field_name="accuracy",
        lookup_expr="gte",
        label="Min Accuracy Score",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Min Accuracy Score"}
        ),
    )
    accuracy_max = django_filters.NumberFilter(
        field_name="accuracy",
        lookup_expr="lte",
        label="Max Accuracy Score",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Max Accuracy Score"}
        ),
    )
    precision_min = django_filters.NumberFilter(
        field_name="precision",
        lookup_expr="gte",
        label="Min Precision Score",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Min Precision Score"}
        ),
    )
    precision_max = django_filters.NumberFilter(
        field_name="precision",
        lookup_expr="lte",
        label="Max Precision Score",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Max Precision Score"}
        ),
    )
    recall_min = django_filters.NumberFilter(
        field_name="recall",
        lookup_expr="gte",
        label="Min Recall Score",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Min Recall Score"}
        ),
    )
    recall_max = django_filters.NumberFilter(
        field_name="recall",
        lookup_expr="lte",
        label="Max Recall Score",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Max Recall Score"}
        ),
    )
    f1_score_min = django_filters.NumberFilter(
        field_name="f1_score",
        lookup_expr="gte",
        label="Min F1 Score Score",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Min F1 Score Score"}
        ),
    )
    f1_score_max = django_filters.NumberFilter(
        field_name="f1_score",
        lookup_expr="lte",
        label="Max F1 Score Score",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Max F1 Score Score"}
        ),
    )
    date_trained_start = django_filters.DateFilter(
        field_name="date_trained",
        lookup_expr="gte",
        label="Date Start",
        widget=DateInput(
            attrs={"class": "form-control", "placeholder": "Submission Date Start"}
        ),
    )
    date_trained_end = django_filters.DateFilter(
        field_name="date_trained",
        lookup_expr="lte",
        label="Date End",
        widget=DateInput(
            attrs={"class": "form-control", "placeholder": "Submission Date End"}
        ),
    )
    is_default = django_filters.ChoiceFilter(
        field_name="is_default",
        label="Is Active",
        choices=[("", "All"), (True, "Yes"), (False, "No")],
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = TrainedModel
        fields = [
            "name",
            "version",
            "model_type",
            "accuracy_min",
            "accuracy_max",
            "precision_min",
            "precision_max",
            "recall_min",
            "recall_max",
            "f1_score_min",
            "f1_score_max",
            "date_trained_start",
            "date_trained_end",
            "is_default",
        ]


class ActivityLogFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(
        field_name="user__username",
        lookup_expr="icontains",
        label="User",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by Username"}
        ),
    )
    action = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Action",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by Action"}
        ),
    )
    ip_address = django_filters.CharFilter(
        lookup_expr="icontains",
        label="IP Address",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by IP Address"}
        ),
    )
    user_agent = django_filters.CharFilter(
        lookup_expr="icontains",
        label="User Agent",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by User Agent"}
        ),
    )

    # Submission Date Start field
    timestamp_start = django_filters.DateFilter(
        field_name="timestamp",
        lookup_expr="gte",
        label="Timestamp Date Start",
        widget=DateInput(
            attrs={"class": "form-control", "placeholder": "Timestamp Date Start"}
        ),
    )

    # Timestamp Date End field
    timestamp_end = django_filters.DateFilter(
        field_name="timestamp",
        lookup_expr="lte",
        label="Timestamp Date End",
        widget=DateInput(
            attrs={"class": "form-control", "placeholder": "Timestamp Date End"}
        ),
    )

    class Meta:
        model = ActivityLog
        fields = [
            "user",
            "action",
            "ip_address",
            "user_agent",
            "timestamp_start",
            "timestamp_end",
        ]


class FeedbackFilterFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(
        lookup_expr="icontains",
        label="User",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by User"}
        ),
    )
    rating = django_filters.ChoiceFilter(
        field_name="rating",
        label="Rating",
        choices=RATE_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    message = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Message",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by Message"}
        ),
    )
    submitted_at_start = django_filters.DateFilter(
        field_name="submitted_at",
        lookup_expr="gte",
        label="Date Start",
        widget=DateInput(
            attrs={"class": "form-control", "placeholder": "Submission Date Start"}
        ),
    )
    submitted_at_end = django_filters.DateFilter(
        field_name="submitted_at",
        lookup_expr="lte",
        label="Date End",
        widget=DateInput(
            attrs={"class": "form-control", "placeholder": "Submission Date End"}
        ),
    )
    show = django_filters.ChoiceFilter(
        field_name="show",
        label="Show",
        choices=[("", "All"), (True, "Public"), (False, "Private")],
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Feedback
        fields = [
            "user",
            "rating",
            "message",
            "submitted_at_start",
            "submitted_at_end",
            "show",
        ]
