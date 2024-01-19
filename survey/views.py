from datetime import timedelta

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from survey.models import SurveyData


@api_view(["GET"])
def user_average_completion_time(request, user_id):
    average_time = get_user_average_completion_time(user_id)

    if average_time > timedelta(0):
        return Response({'average_completion_time': str(average_time)})
    else:
        return Response({'error': 'No completed surveys found for this user.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
def predict_survey_completion(request, survey_id):
    survey_data = SurveyData.objects.filter(survey_id=survey_id, status='active')
    users_completion_average_time = []

    for survey in survey_data:
        user_average_time = get_user_average_completion_time(survey.user_id)
        if user_average_time > timedelta(0):
            users_completion_average_time.append(user_average_time)

    if not users_completion_average_time:
        return Response(
            {'error': 'No data available to predict completion for this survey.'}, status=status.HTTP_404_NOT_FOUND
        )
    else:
        return Response({'predicted_completion_time': str(max(users_completion_average_time))})


def get_user_average_completion_time(user_id):
    survey_data = SurveyData.objects.filter(user_id=user_id, status='finished')
    total_time = timedelta()
    count = 0

    for survey in survey_data:
        if survey.completed_at:
            total_time += survey.completed_at - survey.received_at
            count += 1

    if count > 0:
        return total_time / count
    else:
        return timedelta(0)
