from django.test import TestCase
from django.utils import timezone
from patients.models import (
    QuestionnaireResponse,
    Response,
    PredictionResult,
    Feedback,
    Contact,
)
from accounts.models import Account
from ml.models import ActivityLog


class QuestionnaireResponseModelTest(TestCase):

    def setUp(self):
        self.user = Account.objects.create(
            email="testuser@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            agree=True,
        )
        self.questionnaire_response = QuestionnaireResponse.objects.create(
            user=self.user, progress=50.0, state="Pending"
        )

    def test_str_method(self):
        expected_str = f"{self.user.username} - {self.questionnaire_response.submission_date.strftime('%Y-%m-%d %H:%M:%S')}"
        self.assertEqual(str(self.questionnaire_response), expected_str)

    def test_score_property(self):
        self.assertEqual(
            self.questionnaire_response.score, 0.00
        )  # Expecting 0.00 if no PredictionResult

    def test_result_property(self):
        self.assertIsNone(self.questionnaire_response.result)


class PredictionResultModelTest(TestCase):

    def setUp(self):
        self.user = Account.objects.create(
            email="testuser@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            agree=True,
        )
        self.questionnaire_response = QuestionnaireResponse.objects.create(
            user=self.user, progress=100.0, state="Completed"
        )
        self.prediction_result = PredictionResult.objects.create(
            user=self.user,
            questionnaire_response=self.questionnaire_response,
            dob="1985-06-15",
            risk_level="Low",
            risk_score=25.00,
            probability_benign=90.00,
            probability_malignant=10.00,
            chart_data={},
        )

    def test_str_method(self):
        expected_str = (
            f"Prediction for {self.user.username} at {self.prediction_result.timestamp}"
        )
        self.assertEqual(str(self.prediction_result), expected_str)

    def test_benign_method(self):
        self.assertEqual(self.prediction_result.benign(), "9000.00")

    def test_malignant_method(self):
        self.assertEqual(self.prediction_result.malignant(), "1000.00")

    def test_get_risk_level_method(self):
        self.assertEqual(self.prediction_result.get_risk_level(), "Low Risk Title")


class FeedbackModelTest(TestCase):

    def setUp(self):
        self.user = Account.objects.create(
            email="testuser@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            agree=True,
        )
        self.feedback = Feedback.objects.create(
            user=self.user, rating=5, message="Great service!"
        )

    def test_str_method(self):
        expected_str = (
            f"Feedback from {self.user.full_name()} at {self.feedback.submitted_at}"
        )
        self.assertEqual(str(self.feedback), expected_str)


class ContactModelTest(TestCase):

    def setUp(self):
        self.contact = Contact.objects.create(
            name="John Doe",
            email="johndoe@example.com",
            message="I have a question about your service.",
        )

    def test_str_method(self):
        expected_str = f"Message from {self.contact.name}"
        self.assertEqual(str(self.contact), expected_str)

