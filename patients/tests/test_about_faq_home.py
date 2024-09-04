from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.template import TemplateDoesNotExist


class AboutViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")
        self.url = reverse("about")  # Adjust the name of the URL if necessary

    def test_get_about(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "about.html")
        self.assertContains(response, "About Us")

    def test_user_activity_logged(self):
        # Assuming you have a way to check user activity logs
        self.client.get(self.url)
        # Check that user activity was logged as expected
        # You might need to mock log_user_activity or check the database for entries


class FAQViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")
        self.url = reverse("faqs")  # Adjust the name of the URL if necessary

    def test_get_faqs(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "faqs.html")
        self.assertContains(response, "FAQs")

    def test_ajax_search_faqs(self):
        query = "example"  # Adjust this to match an actual FAQ item
        response = self.client.get(
            self.url, {"q": query}, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        # Verify that the returned JSON data matches expectations
        # For example, check if the filtered_faqs contains items that should match the query


class HomeViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")
        self.url = reverse("homeview")  # Adjust the name of the URL if necessary

    def test_get_home(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")
        self.assertContains(response, "Home")

    def test_user_activity_logged(self):
        # Assuming you have a way to check user activity logs
        self.client.get(self.url)
        # Check that user activity was logged as expected
        # You might need to mock log_user_activity or check the database for entries
