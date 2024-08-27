from django.test import TestCase, Client
from django.urls import reverse_lazy
from django.contrib.auth.models import User, Group
from django.core import mail
from django.contrib import messages
from django.utils.translation import gettext as _
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from ..forms import RegistrationForm  # Adjust the import if needed

User = get_user_model()


class UserRegistrationViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.registration_url = reverse_lazy(
            "auth:register"
        )  # Adjust URL name if necessary

    def test_registration_success(self):
        response = self.client.post(
            self.registration_url,
            {
                "email": "testuser@example.com",
                "password": "testpassword123",
                "confirm_password": "testpassword123",
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirects on success
        self.assertRedirects(response, reverse_lazy("auth:login"))
        self.assertTrue(User.objects.filter(email="testuser@example.com").exists())
        user = User.objects.get(email="testuser@example.com")
        self.assertFalse(
            user.is_active
        )  # User should not be active until they verify their email
        self.assertEqual(user.username, "testuser")

        # Check that an email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn("Activate Your Account", email.subject)
        self.assertIn("testuser@example.com", email.body)

    def test_registration_invalid_form(self):
        response = self.client.post(
            self.registration_url,
            {
                "email": "invalid-email",
                "password": "short",
                "confirm_password": "mismatch",
            },
        )
        self.assertEqual(response.status_code, 200)  # Form should be re-rendered
        self.assertTemplateUsed(response, "accounts/register.html")
        self.assertFormError(
            response, "form", "email", _("Enter a valid email address.")
        )
        self.assertFormError(
            response,
            "form",
            "password",
            _("This password is too short. It must contain at least 8 characters."),
        )
        self.assertFormError(
            response, "form", "confirm_password", _("Passwords do not match.")
        )

    def test_registration_creates_user_group(self):
        self.client.post(
            self.registration_url,
            {
                "email": "testuser@example.com",
                "password": "testpassword123",
                "confirm_password": "testpassword123",
            },
        )
        group = Group.objects.get(name="Users")
        self.assertTrue(group.user_set.filter(email="testuser@example.com").exists())

    def test_registration_logs_user_activity(self):
        with self.assertLogs("django.request", level="INFO") as log:
            self.client.post(
                self.registration_url,
                {
                    "email": "testuser@example.com",
                    "password": "testpassword123",
                    "confirm_password": "testpassword123",
                },
            )
            self.assertIn(
                "signed up", log.output[0]
            )  # Adjust as per actual logging output

    def test_form_invalid(self):
        response = self.client.post(
            self.registration_url,
            {
                "email": "testuser@example.com",
                "password": "testpassword123",
                "confirm_password": "wrongpassword",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Passwords do not match.")

    def test_registration_successful_messages(self):
        response = self.client.post(
            self.registration_url,
            {
                "email": "testuser@example.com",
                "password": "testpassword123",
                "confirm_password": "testpassword123",
            },
        )
        messages_list = list(response.context["messages"])
        self.assertTrue(
            any(
                msg.message == _("Thank you for your registration!")
                for msg in messages_list
            )
        )
