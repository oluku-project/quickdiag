from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from unittest.mock import patch
from patients.models import QuestionnaireResponse, STATE
from patients.views import PendingResultView

class PendingResultViewTest(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')

        # Create test data
        self.in_progress_response = QuestionnaireResponse.objects.create(
            user=self.user,
            state=STATE.IN_PROGRESS,
            submission_date='2024-08-15',
            updated_date='2024-08-16',
            # other fields...
        )
        self.completed_response = QuestionnaireResponse.objects.create(
            user=self.user,
            state=STATE.COMPLETED,
            submission_date='2024-08-15',
            updated_date='2024-08-16',
            # other fields...
        )

    @patch('patients.views.log_user_activity')
    def test_get_pending_results(self, mock_log_user_activity):
        url = reverse('pending_result')
        response = self.client.get(url)

        # Check response status and template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'patients/pending-results.html')

        # Check context data
        self.assertIn('items', response.context)
        self.assertIn('title_root', response.context)
        self.assertEqual(response.context['title_root'], 'Results In Progress')

        # Check that log_user_activity was called
        mock_log_user_activity.assert_called_once_with(
            self.client.request, self.user, 'viewed uncompleted assessment'
        )

        # Check if only in-progress results are in the context
        items = response.context['items']
        self.assertIn(self.in_progress_response, items)
        self.assertNotIn(self.completed_response, items)

### 2. **Test Code for `PendingResultDeleteView`**

from django.http import JsonResponse

class PendingResultDeleteViewTest(TestCase):
    def setUp(self):
        super().setUp()
        # Create a user and test data (same as above)

    @patch('patients.views.log_user_activity')
    def test_delete_result_success(self, mock_log_user_activity):
        # Create a result to delete
        response_to_delete = QuestionnaireResponse.objects.create(
            user=self.user,
            state=STATE.IN_PROGRESS,
            submission_date='2024-08-15',
            updated_date='2024-08-16',
            # other fields...
        )

        # Test the delete request
        url = reverse('pending_result_delete')
        response = self.client.post(url, {'result_id': response_to_delete.id})

        # Check response status and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True, "message": "Result deleted successfully."})

        # Check if the result was deleted
        self.assertFalse(QuestionnaireResponse.objects.filter(id=response_to_delete.id).exists())

        # Check that log_user_activity was called
        mock_log_user_activity.assert_called_once_with(
            self.client.request, self.user, 'deleted pending result'
        )

    @patch('patients.views.log_user_activity')
    def test_delete_result_failure(self, mock_log_user_activity):
        # Test deleting with an invalid ID
        url = reverse('pending_result_delete')
        response = self.client.post(url, {'result_id': 'invalid_id'})

        # Check response status and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": False, "message": "Result unable to delete!"})

        # Check that log_user_activity was called
        mock_log_user_activity.assert_not_called()
