from django.test import TestCase, Client
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from django.contrib.auth.middleware import get_user
from ..models import Account  # Adjust the import if needed

User = get_user_model()


class PrivacyViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.privacy_url = reverse_lazy("auth:privacy")
        self.user = User.objects.create(email="testuser@example.com", is_active=True)
        self.user.set_password("testpassword123")
        self.user.save()
        self.client.login(email="testuser@example.com", password="testpassword123")

    def test_privacy_view(self):
        response = self.client.get(self.privacy_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/privacy.html")
        self.assertIn(_("Privacy"), response.content.decode())
        self.assertIn(
            _("viewed privacy page"), response.content.decode()
        )  # Ensure logging message is included


class TermsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.terms_url = reverse_lazy("auth:terms")
        self.user = User.objects.create(email="testuser@example.com", is_active=True)
        self.user.set_password("testpassword123")
        self.user.save()
        self.client.login(email="testuser@example.com", password="testpassword123")

    def test_terms_view(self):
        response = self.client.get(self.terms_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/terms.html")
        self.assertIn(_("Terms"), response.content.decode())
        self.assertIn(
            _("viewed terms page"), response.content.decode()
        )  # Ensure logging message is included
