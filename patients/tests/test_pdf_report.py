from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
from io import BytesIO
from django.contrib.auth.models import User
from .models import QuestionnaireResponse, PredictionResult
from .views import PDFReportView


class PDFReportViewTest(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client = Client()
        self.client.login(username="testuser", password="testpassword")

        # Create test data
        self.questionnaire_response = QuestionnaireResponse.objects.create(
            user=self.user,
            submission_date="2024-08-15",
            dob="1990-01-01",
            # other fields...
        )
        self.prediction_result = PredictionResult.objects.create(
            questionnaire_response=self.questionnaire_response,
            risk_score=75,
            probability_benign=0.25,
            probability_malignant=0.75,
            chart_data={
                "categories": ["A", "B", "C"],
                "mean": [10, 20, 30],
                "standard": [1, 2, 3],
                "worst": [5, 15, 25],
            },
            # other fields...
        )

    @patch("patients.views.PDFReportView.get_data")
    @patch("patients.views.PDFReportView.generate_chart")
    def test_generate_pdf(self, mock_generate_chart, mock_get_data):
        # Mock methods
        mock_get_data.return_value = {
            "risk_level": {
                "info": "High",
                "recommendations": [],
                "next": "Next steps",
                "next_steps": [],
            },
            "risk_score": 75,
            "score": 75,
            "probability_benign": 0.25,
            "probability_malignant": 0.75,
            "chart_data": {
                "categories": ["A", "B", "C"],
                "mean": [10, 20, 30],
                "standard": [1, 2, 3],
                "worst": [5, 15, 25],
            },
            "response_instance": self.prediction_result,
        }
        mock_generate_chart.return_value = "mocked_chart_base64"

        # Test the response
        url = reverse("pdf_report_view")
        response = self.client.get(url)

        # Check response status and content type
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")

        # Check that the PDF is being generated
        self.assertTrue(response.content)


class PDFReportDownloadViewTest(TestCase):
    def setUp(self):
        super().setUp()
        # Create a user and test data (same as above)

    @patch("patients.views.PDFReportView.generate_pdf")
    def test_download_pdf(self, mock_generate_pdf):
        # Mock method
        mock_generate_pdf.return_value = b"mocked_pdf_content"

        # Test the download response
        url = reverse("pdf_report_download")
        response = self.client.get(url)

        # Check response status and headers
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Disposition"],
            'attachment; filename="testuser-report.pdf"',
        )
        self.assertEqual(response["Content-Type"], "application/pdf")

        # Check that the PDF content is correct
        self.assertEqual(response.content, b"mocked_pdf_content")


class PDFReportPrintViewTest(TestCase):
    def setUp(self):
        super().setUp()
        # Create a user and test data (same as above)

    @patch("patients.views.PDFReportView.generate_pdf")
    def test_print_pdf(self, mock_generate_pdf):
        # Mock method
        mock_generate_pdf.return_value = b"mocked_pdf_content"

        # Test the inline response
        url = reverse("pdf_report_print")
        response = self.client.get(url)

        # Check response status and headers
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Disposition"], 'inline; filename="testuser-report.pdf"'
        )
        self.assertEqual(response["Content-Type"], "application/pdf")

        # Check that the PDF content is correct
        self.assertEqual(response.content, b"mocked_pdf_content")
