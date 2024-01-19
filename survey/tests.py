from datetime import timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from survey.models import Survey, SurveyData


class SurveyAPITest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='api_test_user1', password='12345')
        self.user2 = User.objects.create_user(username='api_test_user2', password='12345')
        self.survey1 = Survey.objects.create(title='API Test Survey')
        self.survey2 = Survey.objects.create(title='API Test Survey2')
        self.survey3 = Survey.objects.create(title='API Test Survey3')
        self.survey_data = SurveyData.objects.create(user=self.user1, survey=self.survey1, status='active')
        self.survey_data = SurveyData.objects.create(user=self.user2, survey=self.survey1, status='active')

    def test_average_completion_time_user_has_no_completed_surveys(self):
        url = reverse('user_average_completion_time', args=[self.user1.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], 'No completed surveys found for this user.')

    def test_average_completion_time(self):
        survey_received_at = timezone.now()
        SurveyData.objects.create(
            user=self.user1,
            survey=self.survey2,
            status='finished',
            received_at=survey_received_at,
            completed_at=survey_received_at + timedelta(days=2)
        )
        SurveyData.objects.create(
            user=self.user1,
            survey=self.survey3,
            status='finished',
            received_at=survey_received_at,
            completed_at=survey_received_at + timedelta(days=4)
        )

        url = reverse('user_average_completion_time', args=[self.user1.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["average_completion_time"], '3 days, 0:00:00')

    def test_predict_survey_completion_survey_users_has_no_completed_surveys(self):
        url = reverse('predict_survey_completion', args=[self.survey1.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], 'No data available to predict completion for this survey.')

    def test_predict_survey_completion_survey_not_sent_to_any_users(self):
        survey2 = Survey.objects.create(title='API Test Survey2')

        url = reverse('predict_survey_completion', args=[survey2.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], 'No data available to predict completion for this survey.')

    def test_predict_survey_completion(self):
        survey_received_at = timezone.now()
        SurveyData.objects.create(
            user=self.user1,
            survey=self.survey2,
            status='finished',
            received_at=survey_received_at,
            completed_at=survey_received_at + timedelta(days=3)
        )
        SurveyData.objects.create(
            user=self.user2,
            survey=self.survey2,
            status='finished',
            received_at=survey_received_at,
            completed_at=survey_received_at + timedelta(days=4)
        )

        url = reverse('predict_survey_completion', args=[self.survey1.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["predicted_completion_time"], '4 days, 0:00:00')

