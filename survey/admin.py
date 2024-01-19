from django.contrib import admin

from survey.models import Survey, SurveyData

admin.site.register(Survey)
admin.site.register(SurveyData)
