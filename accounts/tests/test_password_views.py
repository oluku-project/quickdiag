from django.test import TestCase, Client
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.core import mail

User = get_user_model()


class ForgotPasswordViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.forgot_password_url = reverse_lazy("auth:forgotPassword")
        self.user = User.objects.create(email="testuser@example.com", is_active=True)
        self.user.set_password("testpassword123")
        self.user.save()

    def test_forgot_password_email_sent(self):
        response = self.client.post(
            self.forgot_password_url, {"email": "testuser@example.com"}
        )
        self.assertEqual(response.status_code, 302)  # Redirects on success
        self.assertRedirects(response, reverse_lazy("auth:login"))
        self.assertIn(
            _("Password reset email has been sent to your email address."),
            [msg.message for msg in response.context["messages"]],
        )
        self.assertEqual(len(mail.outbox), 1)  # One email should be sent
        self.assertIn("Reset Your Password", mail.outbox[0].subject)

    def test_forgot_password_invalid_email(self):
        response = self.client.post(
            self.forgot_password_url, {"email": "nonexistent@example.com"}
        )
        self.assertEqual(response.status_code, 302)  # Redirects on failure
        self.assertRedirects(response, reverse_lazy("auth:forgotPassword"))
        self.assertIn(
            _("Account does not exist!"),
            [msg.message for msg in response.context["messages"]],
        )
        self.assertEqual(len(mail.outbox), 0)  # No email should be sent


class PasswordResetConfirmViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(email="testuser@example.com", is_active=True)
        self.user.set_password("oldpassword123")
        self.user.save()
        self.client.login(email="testuser@example.com", password="oldpassword123")
        self.uid = urlsafe_base64_encode(self.user.pk.encode())
        self.token = default_token_generator.make_token(self.user)
        self.reset_confirm_url = reverse_lazy(
            "auth:password_reset_confirm",
            kwargs={"uidb64": self.uid, "token": self.token},
        )

    def test_password_reset_success(self):
        response = self.client.post(
            self.reset_confirm_url,
            {"new_password1": "newpassword123", "new_password2": "newpassword123"},
        )
        self.assertEqual(response.status_code, 302)  # Redirects on success
        self.assertRedirects(response, reverse_lazy("auth:password_reset_complete"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword123"))
        self.assertIn(
            _(
                "Your password has been reset successfully. You can now log in with your new password."
            ),
            [msg.message for msg in response.context["messages"]],
        )

    def test_password_reset_invalid(self):
        response = self.client.post(
            self.reset_confirm_url,
            {"new_password1": "newpassword123", "new_password2": "differentpassword"},
        )
        self.assertEqual(response.status_code, 200)  # Form re-rendered on failure
        self.assertIn(
            _("new_password2: The two password fields must match."),
            [msg.message for msg in response.context["messages"]],
        )
        self.assertTemplateUsed(response, "accounts/password_reset_confirm.html")


class PasswordResetCompleteViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.reset_complete_url = reverse_lazy("auth:password_reset_complete")

    def test_password_reset_complete(self):
        response = self.client.get(self.reset_complete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/password_reset_complete.html")
        self.assertIn(
            _("Password Reset Complete - Breast Cancer Prediction"),
            response.content.decode(),
        )
