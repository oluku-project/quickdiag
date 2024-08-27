from django.test import TestCase, Client
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import outbox
from django.utils.translation import gettext as _
from patients.models import Account  # Adjust the import if needed
from patients.forms import LoginForm  # Adjust the import if needed

User = get_user_model()


class ActivateAccountViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.activate_url = reverse_lazy("auth:activate_account")

    def test_activate_account_success(self):
        user = User.objects.create(email="testuser@example.com", is_active=False)
        uid = urlsafe_base64_encode(user.pk.encode())
        token = default_token_generator.make_token(user)
        url = f"{self.activate_url}/{uid}/{token}/"

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirects on success
        self.assertRedirects(response, reverse_lazy("auth:login"))
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertIn(
            _("Congratulations! Your account is activated."),
            [msg.message for msg in response.context["messages"]],
        )

    def test_activate_account_invalid_link(self):
        url = f"{self.activate_url}/invalid_uid/invalid_token/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirects on failure
        self.assertRedirects(response, reverse_lazy("auth:signup"))
        self.assertIn(
            _("Invalid activation link"),
            [msg.message for msg in response.context["messages"]],
        )


class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse_lazy("auth:login")
        self.user = User.objects.create(email="testuser@example.com", is_active=True)
        self.user.set_password("testpassword123")
        self.user.save()

    def test_login_success(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "testuser@example.com",
                "password": "testpassword123",
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirects on success
        self.assertRedirects(response, reverse_lazy("auth:user_dashboard"))
        self.assertIn(
            _("You are now logged in."),
            [msg.message for msg in response.context["messages"]],
        )
        self.assertEqual(str(self.client.session["_auth_user_id"]), str(self.user.pk))

    def test_login_invalid_credentials(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "testuser@example.com",
                "password": "wrongpassword",
            },
        )
        self.assertEqual(response.status_code, 200)  # Form re-rendered on failure
        self.assertIn(
            _("Invalid login credentials."),
            [msg.message for msg in response.context["messages"]],
        )
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_login_inactive_account(self):
        user = User.objects.create(email="inactiveuser@example.com", is_active=False)
        user.set_password("testpassword123")
        user.save()
        response = self.client.post(
            self.login_url,
            {
                "username": "inactiveuser@example.com",
                "password": "testpassword123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            _(
                "Your account is inactive. Please check your email for activation instructions."
            ),
            [msg.message for msg in response.context["messages"]],
        )
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_login_invalid_email(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "nonexistent@example.com",
                "password": "testpassword123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            _("Invalid email address. Please try again."),
            [msg.message for msg in response.context["messages"]],
        )
        self.assertTemplateUsed(response, "accounts/login.html")


class LogoutViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.logout_url = reverse_lazy("auth:logout")
        self.user = User.objects.create(email="testuser@example.com", is_active=True)
        self.user.set_password("testpassword123")
        self.user.save()
        self.client.login(email="testuser@example.com", password="testpassword123")

    def test_logout_success(self):
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)  # Redirects on success
        self.assertRedirects(response, reverse_lazy("auth:login"))
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertIn(
            _("You are logged out."),
            [msg.message for msg in response.context["messages"]],
        )
