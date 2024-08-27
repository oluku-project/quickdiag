import datetime
import django_filters
from django import forms

from patients.models import PredictionResult
from accounts.models import CountryChoices, Gender


class DateInput(forms.DateInput):
    input_type = "date"


class PredictionResultFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(
        field_name="user__username",
        lookup_expr="icontains",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by Username"}
        ),
    )
    risk_level = django_filters.ChoiceFilter(
        field_name="risk_level",
        choices=[("Low", "Low"), ("Medium", "Medium"), ("High", "High")],
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    gender = django_filters.ChoiceFilter(
        field_name="user__gender",
        choices=Gender.choices,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    country = django_filters.ChoiceFilter(
        field_name="user__country",
        choices=CountryChoices.as_choices(),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    risk_score_min = django_filters.NumberFilter(
        field_name="risk_score",
        lookup_expr="gte",
        label="Min Risk Score",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Min Risk Score"}
        ),
    )
    risk_score_max = django_filters.NumberFilter(
        field_name="risk_score",
        lookup_expr="lte",
        label="Max Risk Score",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Max Risk Score"}
        ),
    )
    probability_benign_min = django_filters.NumberFilter(
        field_name="probability_benign",
        lookup_expr="gte",
        label="Min Probability Benign",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Min Probability Benign"}
        ),
    )
    probability_benign_max = django_filters.NumberFilter(
        field_name="probability_benign",
        lookup_expr="lte",
        label="Max Probability Benign",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Max Probability Benign"}
        ),
    )
    probability_malignant_min = django_filters.NumberFilter(
        field_name="probability_malignant",
        lookup_expr="gte",
        label="Min Probability Malignant",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Min Probability Malignant"}
        ),
    )
    probability_malignant_max = django_filters.NumberFilter(
        field_name="probability_malignant",
        lookup_expr="lte",
        label="Max Probability Malignant",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Max Probability Malignant"}
        ),
    )
    submission_date_start = django_filters.DateFilter(
        field_name="submission_date",
        lookup_expr="gte",
        label="Submission Date Start",
        widget=DateInput(
            attrs={"class": "form-control", "placeholder": "Submission Date Start"}
        ),
    )
    submission_date_end = django_filters.DateFilter(
        field_name="submission_date",
        lookup_expr="lte",
        label="Submission Date End",
        widget=DateInput(
            attrs={"class": "form-control", "placeholder": "Submission Date End"}
        ),
    )
    dob_start = django_filters.DateFilter(
        field_name="user__dob",
        lookup_expr="gte",
        label="Date of Birth Start",
        widget=DateInput(
            attrs={"class": "form-control", "placeholder": "Date of Birth Start"}
        ),
    )
    dob_end = django_filters.DateFilter(
        field_name="user__dob",
        lookup_expr="lte",
        label="Date of Birth End",
        widget=DateInput(
            attrs={"class": "form-control", "placeholder": "Date of Birth End"}
        ),
    )
    min_age = django_filters.NumberFilter(
        method="filter_min_age",
        label="Min Age",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Min Age"}
        ),
    )
    max_age = django_filters.NumberFilter(
        method="filter_max_age",
        label="Max Age",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Max Age"}
        ),
    )

    class Meta:
        model = PredictionResult
        fields = [
            "user",
            "risk_level",
            "gender",
            "country",
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

    def filter_min_age(self, queryset, name, value):
        now = datetime.datetime.now()
        min_dob = now - datetime.timedelta(days=int(value) * 365.25)
        return queryset.filter(user__dob__lte=min_dob)

    def filter_max_age(self, queryset, name, value):
        now = datetime.datetime.now()
        max_dob = now - datetime.timedelta(days=int(value) * 365.25)
        return queryset.filter(user__dob__gte=max_dob)
