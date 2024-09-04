from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from patients.models import Questionnaire
from patients.views import QuestionnaireView


class QuestionnaireViewTestCase(TestCase):

    def setUp(self):
        # Set up test data
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.questionnaire = Questionnaire.objects.create(
            title="Test Questionnaire",
            description="A test description",
            created_by=self.user,
        )
        self.url = reverse("questionnaire_detail", args=[self.questionnaire.pk])

    def test_questionnaire_view_unauthenticated(self):
        # Test that an unauthenticated user is redirected
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"/accounts/login/?next={self.url}")

    def test_questionnaire_view_authenticated(self):
        # Log in the user
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "questionnaire_detail.html")
        self.assertContains(response, self.questionnaire.title)
        self.assertContains(response, self.questionnaire.description)

    def test_questionnaire_view_context(self):
        # Log in the user
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(self.url)
        self.assertIn("questionnaire", response.context)
        self.assertEqual(response.context["questionnaire"], self.questionnaire)


"""
python manage.py test my_app.tests.test_views
This command will run all the test cases in the test_views.py file under the my_app/tests directory.

4. Advanced Tips
Fixtures: Use fixtures to load predefined data into your database before running tests.
Factories: Use factory_boy to create complex test data with less boilerplate.
Mocking: Use the unittest.mock module to mock external dependencies or isolate the unit being tested.
Parallel Testing: If you have many tests, consider using Django's parallel testing feature to speed up the testing process.
By organizing your tests in this manner, you maintain a clean and modular test suite, making it easier to manage and expand as your project grows.
"""

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from unittest.mock import patch, MagicMock

from patients.models import QuestionnaireResponse, STATE
from patients.views import SummaryView
from ml.utils import log_user_activity

User = get_user_model()


class SummaryViewTest(TestCase):
    def setUp(self):
        # Create a user and assign permissions if necessary
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="password123",
        )
        self.user.user_permissions.add(
            Permission.objects.get(codename="view_questionnaireresponse")
        )
        self.client.login(email="testuser@example.com", password="password123")

        # Create a QuestionnaireResponse instance
        self.questionnaire_response = QuestionnaireResponse.objects.create(
            user=self.user, progress=50.0, state=STATE.PENDING
        )

        self.url = reverse("summary", kwargs={"pk": self.questionnaire_response.pk})
        self.factory = RequestFactory()

    @patch("patients.views.SummaryView.fetchRespondedQuestions")
    @patch("ml.utils.log_user_activity")
    def test_get_context_data(
        self, mock_log_user_activity, mock_fetch_responded_questions
    ):
        # Mock fetchRespondedQuestions to return expected data
        mock_fetch_responded_questions.return_value = {
            "question1": "Answer1",
            "question2": "Answer2",
        }

        request = self.factory.get(self.url)
        request.user = self.user
        response = SummaryView.as_view()(request, pk=self.questionnaire_response.pk)

        # Check if the context contains the expected data
        self.assertEqual(
            response.context_data["response_instance"], self.questionnaire_response
        )
        self.assertEqual(
            response.context_data["grouped_questions"],
            {"question1": "Answer1", "question2": "Answer2"},
        )
        self.assertEqual(response.context_data["title_root"], "Summary")

        # Check if the state of the QuestionnaireResponse was updated
        self.questionnaire_response.refresh_from_db()
        self.assertEqual(self.questionnaire_response.state, STATE.PENDING)

        # Check if log_user_activity was called
        mock_log_user_activity.assert_called_once_with(
            request, self.user, "viewed summary on assessment"
        )

    def test_view_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_view_redirect_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/accounts/login/?next={self.url}")

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from unittest.mock import patch, MagicMock
import pandas as pd
import pickle

from patients.models import QuestionnaireResponse, PredictionResult, STATE
from patients.views import PredictionView
from ml.utils import log_user_activity

User = get_user_model()


class PredictionViewTest(TestCase):
    def setUp(self):
        # Create a user and assign permissions if necessary
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="password123",
        )
        self.user.user_permissions.add(
            Permission.objects.get(codename="view_questionnaireresponse")
        )
        self.client.login(email="testuser@example.com", password="password123")

        # Create a QuestionnaireResponse instance
        self.questionnaire_response = QuestionnaireResponse.objects.create(
            user=self.user, progress=50.0, state=STATE.PENDING
        )

        self.url = reverse(
            "detailed_result", kwargs={"pk": self.questionnaire_response.pk}
        )
        self.factory = RequestFactory()

    @patch("patients.views.PredictionView.get_queryset")
    @patch("patients.views.PredictionView.get_object")
    def test_get_queryset_and_object(self, mock_get_object, mock_get_queryset):
        mock_get_queryset.return_value = PredictionResult.objects.all()
        mock_get_object.return_value = self.questionnaire_response

        request = self.factory.get(self.url)
        request.user = self.user
        response = PredictionView.as_view()(request, pk=self.questionnaire_response.pk)

        self.assertEqual(
            response.context_data["response_instance"], self.questionnaire_response
        )
        mock_get_queryset.assert_called_once()
        mock_get_object.assert_called_once_with(queryset=mock_get_queryset.return_value)

    @patch("patients.views.PredictionView.get_clean_data")
    @patch("patients.views.PredictionView.get_default_values")
    @patch("patients.views.PredictionView.add_predictions")
    @patch("patients.views.PredictionView.get_line_scatter_chart")
    @patch("patients.views.PredictionView.save_prediction_result")
    @patch("patients.views.PredictionView.make_prediction")
    @patch("ml.utils.log_user_activity")
    def test_get_context_data(
        self,
        mock_log_user_activity,
        mock_make_prediction,
        mock_save_prediction_result,
        mock_get_line_scatter_chart,
        mock_add_predictions,
        mock_get_default_values,
        mock_get_clean_data,
    ):
        # Mock data
        mock_get_clean_data.return_value = pd.DataFrame(
            {"radius_mean": [0.1, 0.2], "texture_mean": [0.2, 0.3], "diagnosis": [1, 0]}
        )
        mock_get_default_values.return_value = {"radius_mean": 0.15}
        mock_add_predictions.return_value = [[0.2, 0.8]]
        mock_get_line_scatter_chart.return_value = {
            "categories": ["A", "B"],
            "mean": [0.1],
            "standard": [0.2],
            "worst": [0.3],
        }
        mock_make_prediction.return_value = ("High", 0.75)

        request = self.factory.get(self.url)
        request.user = self.user
        response = PredictionView.as_view()(request, pk=self.questionnaire_response.pk)

        # Check context data
        self.assertEqual(
            response.context_data["response_instance"], self.questionnaire_response
        )
        self.assertEqual(response.context_data["risk_level"], "High")
        self.assertEqual(response.context_data["risk_score"], "75.00")
        self.assertEqual(response.context_data["probability_benign"], "20.00")
        self.assertEqual(response.context_data["probability_malignant"], "80.00")
        self.assertEqual(
            response.context_data["chart_data"],
            {
                "categories": ["A", "B"],
                "mean": [0.1],
                "standard": [0.2],
                "worst": [0.3],
            },
        )
        self.assertEqual(response.context_data["title_root"], "Result")

        # Check if log_user_activity was called
        mock_log_user_activity.assert_called_once_with(
            request, self.user, "completed an assessment"
        )

    def test_store_data_in_session(self):
        request = self.factory.get(self.url)
        request.user = self.user
        view = PredictionView()
        view.request = request

        # Mock the session
        view.storeDataInSession(self.questionnaire_response, "detailed_result")
        self.assertEqual(
            request.session["input_data"],
            {"url_name": "detailed_result", "pk": self.questionnaire_response.pk},
        )

    @patch("patients.views.PredictionView.get_clean_data")
    @patch("patients.views.PredictionView.get_default_values")
    @patch("patients.views.PredictionView.add_predictions")
    @patch("patients.views.PredictionView.get_line_scatter_chart")
    @patch("patients.views.PredictionView.save_prediction_result")
    @patch("patients.views.PredictionView.make_prediction")
    @patch("ml.utils.log_user_activity")
    def test_view_status_code(
        self,
        mock_log_user_activity,
        mock_make_prediction,
        mock_save_prediction_result,
        mock_get_line_scatter_chart,
        mock_add_predictions,
        mock_get_default_values,
        mock_get_clean_data,
    ):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_view_redirect_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/accounts/login/?next={self.url}")


from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.http import JsonResponse
from .models import PredictionResult
from .views import PredictionResultView, PredictionResultDeleteView


class PredictionResultViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")
        self.url = reverse("result_hostores")  # Adjust the URL name as needed

        # Create some PredictionResults for testing
        self.results = [
            PredictionResult.objects.create(
                user=self.user, risk_score=50, deleted=False
            ),
            PredictionResult.objects.create(
                user=self.user, risk_score=60, deleted=False
            ),
        ]

    def test_prediction_result_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "patients/result-histores.html")
        self.assertContains(response, "Prediction Results")
        for result in self.results:
            self.assertContains(response, result.risk_score)

    def test_context_data(self):
        response = self.client.get(self.url)
        self.assertIn("title_root", response.context)
        self.assertEqual(response.context["title_root"], "Prediction Results")


class PredictionResultDeleteViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        # Create a PredictionResult for testing
        self.result = PredictionResult.objects.create(
            user=self.user, risk_score=50, deleted=False
        )
        self.url = reverse("resultdelete_view")  # Adjust the URL name as needed

    def test_delete_prediction_result(self):
        response = self.client.post(self.url, {"result_id": self.result.id})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": True, "message": "Result deleted successfully."},
        )

        # Verify the result was marked as deleted
        self.result.refresh_from_db()
        self.assertTrue(self.result.deleted)

    def test_delete_prediction_result_failure(self):
        response = self.client.post(self.url, {"result_id": "invalid"})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content, {"success": False, "message": "Resulte unable to delete!"}
        )

        # Verify no result was deleted
        self.result.refresh_from_db()
        self.assertFalse(self.result.deleted)
