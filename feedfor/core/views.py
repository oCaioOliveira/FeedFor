import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from weasyprint import HTML

from .models import Student, Questionnaire, Item
from .feedback import check_answers, generate_formative_feedback
from .utils import send_feedback_email

class SubmitQuestionnaireView(APIView):
    def post(self, request):
        email = request.data.get('email')
        name = request.data.get('name')
        content = request.data.get('content')
        external_id = request.data.get('external_id')
        items_data = request.data.get('items', [])

        student, _ = Student.objects.get_or_create(email=email)

        questionnaire = Questionnaire.objects.create(
            name=name,
            content=content,
            external_id=external_id,
            student=student
        )

        for item_data in items_data:
            Item.objects.create(
                questionnaire=questionnaire,
                question=item_data.get('question'),
                answer=item_data.get('answer'),
                subcontent=item_data.get('subcontent'),
                correct_answer=item_data.get('correct_answer')
            )

        feedbacks = check_answers(items_data)
        formative_feedback = generate_formative_feedback(feedbacks, content)

        send_feedback_email(email, questionnaire.name, formative_feedback)

        return Response({'message': 'Questionnaire submitted successfully'}, status=status.HTTP_201_CREATED)