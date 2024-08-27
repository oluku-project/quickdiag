from django.test import TestCase, Client
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib import messages
from django.utils.translation import gettext as _
from patients.models import PredictionResult, Account  # Adjust the import if needed
from patients.forms import UpdateAccountForm, SetPasswordForm
from django.contrib.auth import get_user_model
from django.db.models import Sum, Avg
from django.db.models.functions import TruncMonth

User = get_user_model()


class UserDashboardViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.dashboard_url = reverse_lazy("auth:user_dashboard")
        self.user = User.objects.create(email="testuser@example.com", is_active=True)
        self.user.set_password("testpassword123")
        self.user.save()
        self.client.login(email="testuser@example.com", password="testpassword123")

        # Setup PredictionResult data
        PredictionResult.objects.create(
            user=self.user,
            risk_score=75.0,
            risk_level="High",
            submission_date="2024-08-15",
        )
        PredictionResult.objects.create(
            user=self.user,
            risk_score=50.0,
            risk_level="Moderate",
            submission_date="2024-08-16",
        )

    def test_user_dashboard_view(self):
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/user-dashboard.html")

        # Check that context data is passed correctly
        self.assertIn("area_chart_data", response.context)
        self.assertIn("avg_chart_data", response.context)
        self.assertIn("donut_chart_data", response.context)
        self.assertIn("overall_risk_score", response.context)
        self.assertIn("total_predictions", response.context)
        self.assertIn("high_risk_predictions", response.context)
        self.assertIn("last_prediction_date", response.context)
        self.assertIn("result", response.context)
        self.assertIn(_("User Dashboard"), response.content.decode())
        self.assertIn(
            _("viewed dashboard page"), response.content.decode()
        )  # Ensure logging message is included


class UpdateAccountViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.profile_url = reverse_lazy("auth:profile")
        self.user = User.objects.create(email="testuser@example.com", is_active=True)
        self.user.set_password("testpassword123")
        self.user.save()
        self.client.login(email="testuser@example.com", password="testpassword123")

    def test_get_update_account_view(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile.html")
        self.assertIn("update_form", response.context)
        self.assertIn("password_form", response.context)
        self.assertIn("validity", response.context)
        self.assertIn(_("Profile"), response.content.decode())

    def test_post_update_profile(self):
        response = self.client.post(
            self.profile_url,
            {
                "update_profile": True,
                "first_name": "NewFirstName",
                "last_name": "NewLastName",
            },
        )
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "NewFirstName")
        self.assertEqual(self.user.last_name, "NewLastName")
        self.assertIn(
            _("Account updated successfully"), response.cookies.get("messages").value
        )

    def test_post_change_password(self):
        response = self.client.post(
            self.profile_url,
            {
                "change_password": True,
                "old_password": "testpassword123",
                "new_password1": "newpassword123",
                "new_password2": "newpassword123",
            },
        )
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.client.logout()
        self.client.login(email="testuser@example.com", password="newpassword123")
        self.assertTrue(
            self.client.login(email="testuser@example.com", password="newpassword123")
        )
        self.assertIn(
            _("Password updated successfully"), response.cookies.get("messages").value
        )
