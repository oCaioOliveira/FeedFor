from django.urls import path
from .views import SendFeedbackView, ResendFeedbackView

urlpatterns = [
    path("send-feedback/", SendFeedbackView.as_view(), name="send-feedback"),
    path("resend-feedback/", ResendFeedbackView.as_view(), name="resend-feedback"),
]
