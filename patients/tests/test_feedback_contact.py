from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from patients.models import Feedback, ContactMessage
from patients.forms import FeedbackForm, ContactForm


class FeedbackViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")
        self.url = reverse("feedback")  # Adjust the name of the URL if necessary

    def test_post_valid_feedback(self):
        data = {"message": "This is a feedback message."}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": True, "message": "Thank you for your feedback!"},
        )
        self.assertTrue(Feedback.objects.filter(user=self.user).exists())

    def test_post_invalid_feedback(self):
        data = {"message": ""}  # Assuming 'message' is a required field
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": False, "errors": {"message": ["This field is required."]}},
        )


class ContactViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")
        self.url = reverse("contactview")  # Adjust the name of the URL if necessary

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact.html")
        self.assertContains(response, "Contact")

    def test_post_valid_contact(self):
        data = {"subject": "Test subject", "message": "This is a contact message."}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": True, "message": "Thank you for your message!"},
        )
        self.assertTrue(ContactMessage.objects.filter(user=self.user).exists())

    def test_post_invalid_contact(self):
        data = {"subject": "", "message": ""}  # Assuming these fields are required
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "success": False,
                "errors": {
                    "subject": ["This field is required."],
                    "message": ["This field is required."],
                },
            },
        )
# python manage.py test
