from django import forms
from .models import EmailSettings


class EmailSettingsForm(forms.ModelForm):
    class Meta:
        model = EmailSettings
        fields = [
            "email_backend",
            "email_host",
            "email_port",
            "email_use_tls",
            "email_use_ssl",
            "email_host_user",
            "email_host_password",
            "default_from_email",
            "email_subject_prefix",
        ]
        widgets = {
            "email_backend": forms.TextInput(attrs={"class": "form-control"}),
            "email_host": forms.TextInput(attrs={"class": "form-control"}),
            "email_port": forms.NumberInput(attrs={"class": "form-control"}),
            "email_use_tls": forms.CheckboxInput(attrs={"class": "chk-col-primary"}),
            "email_use_ssl": forms.CheckboxInput(attrs={"class": "chk-col-primary"}),
            "email_host_user": forms.TextInput(attrs={"class": "form-control"}),
            "email_host_password": forms.PasswordInput(attrs={"class": "form-control"}),
            "default_from_email": forms.EmailInput(attrs={"class": "form-control"}),
            "email_subject_prefix": forms.TextInput(attrs={"class": "form-control"}),
        }


from django import forms
from .models import GeneralSettings


class GeneralSettingsForm(forms.ModelForm):
    class Meta:
        model = GeneralSettings
        fields = [
            "allow_registration",
            "maintenance_mode",
            "maintenance_end_time",
            "contact_email",
            "site_name",
            "telephone",
            "company",
            "address",
            "tagline",
            "maintenance_message",
            "site_description",
        ]
        widgets = {
            "allow_registration": forms.CheckboxInput(
                attrs={"class": "chk-col-primary"}
            ),
            "maintenance_mode": forms.CheckboxInput(attrs={"class": "chk-col-primary"}),
            "maintenance_end_time": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
            "maintenance_message": forms.Textarea(attrs={"class": "form-control"}),
            "contact_email": forms.EmailInput(attrs={"class": "form-control"}),
            "telephone": forms.EmailInput(attrs={"class": "form-control"}),
            "address": forms.EmailInput(attrs={"class": "form-control"}),
            "site_name": forms.TextInput(attrs={"class": "form-control"}),
            "company": forms.TextInput(attrs={"class": "form-control"}),
            "tagline": forms.TextInput(attrs={"class": "form-control"}),
            "site_description": forms.Textarea(attrs={"class": "form-control"}),
        }
