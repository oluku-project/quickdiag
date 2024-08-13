import django_filters
from django import forms
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Account, CountryChoices, Gender


class DateInput(forms.DateInput):
    input_type = "date"


class AccountFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(
        field_name="first_name",
        lookup_expr="icontains",
        label="First Name",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by First Name"}
        ),
    )
    last_name = django_filters.CharFilter(
        field_name="last_name",
        lookup_expr="icontains",
        label="Last Name",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by Last Name"}
        ),
    )
    username = django_filters.CharFilter(
        field_name="username",
        lookup_expr="icontains",
        label="Username",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by Username"}
        ),
    )
    email = django_filters.CharFilter(
        field_name="email",
        lookup_expr="icontains",
        label="Email",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by Email"}
        ),
    )
    gender = django_filters.ChoiceFilter(
        field_name="gender",
        choices=Gender.choices,
        label="Gender",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    country = django_filters.ChoiceFilter(
        field_name="country",
        choices=CountryChoices.as_choices(),
        label="Country",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    date_joined_start = django_filters.DateFilter(
        field_name="date_joined",
        lookup_expr="gte",
        label="Joined After",
        widget=DateInput(
            attrs={"class": "form-control", "placeholder": "Joined After"}
        ),
    )
    date_joined_end = django_filters.DateFilter(
        field_name="date_joined",
        lookup_expr="lte",
        label="Joined Before",
        widget=DateInput(
            attrs={"class": "form-control", "placeholder": "Joined Before"}
        ),
    )
    last_login_start = django_filters.DateFilter(
        field_name="last_login",
        lookup_expr="gte",
        label="Last Login After",
        widget=DateInput(
            attrs={"class": "form-control", "placeholder": "Last Login After"}
        ),
    )
    last_login_end = django_filters.DateFilter(
        field_name="last_login",
        lookup_expr="lte",
        label="Last Login Before",
        widget=DateInput(
            attrs={"class": "form-control", "placeholder": "Last Login Before"}
        ),
    )
    is_active = django_filters.BooleanFilter(
        field_name="is_active",
        label="Is Active",
        widget=forms.Select(
            choices=[(True, "Yes"), (False, "No")],
            attrs={"class": "form-control"},
        ),
    )
    is_staff = django_filters.BooleanFilter(
        field_name="is_staff",
        label="Is Staff",
        widget=forms.Select(
            choices=[(True, "Yes"), (False, "No")],
            attrs={"class": "form-control"},
        ),
    )
    is_superadmin = django_filters.BooleanFilter(
        field_name="is_superadmin",
        label="Is Super Admin",
        widget=forms.Select(
            choices=[(True, "Yes"), (False, "No")],
            attrs={"class": "form-control"},
        ),
    )
    min_age = django_filters.NumberFilter(
        method="filter_min_age",
        label="Minimum Age",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Min Age"}
        ),
    )
    max_age = django_filters.NumberFilter(
        method="filter_max_age",
        label="Maximum Age",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Max Age"}
        ),
    )

    class Meta:
        model = Account
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "gender",
            "country",
            "date_joined_start",
            "date_joined_end",
            "last_login_start",
            "last_login_end",
            "is_active",
            "is_staff",
            "is_superadmin",
            "min_age",
            "max_age",
        ]

    def filter_min_age(self, queryset, name, value):
        min_birth_date = timezone.now().date() - timedelta(days=int(value) * 365.25)
        return queryset.filter(date_of_birth__lte=min_birth_date)

    def filter_max_age(self, queryset, name, value):
        max_birth_date = timezone.now().date() - timedelta(days=int(value) * 365.25)
        return queryset.filter(date_of_birth__gte=max_birth_date)
