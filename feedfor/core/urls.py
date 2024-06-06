from django.urls import path
from .views import SubmitQuestionnaireView

urlpatterns = [
    path('submit-questionnaire/', SubmitQuestionnaireView.as_view(), name='submit-questionnaire'),
]