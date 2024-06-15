import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from weasyprint import HTML

from .models import Student, Questionnaire, Item, Answer
from .feedback import check_answers, generate_formative_feedback
from .tasks import send_feedback_email


class SubmitQuestionnaireView(APIView):
    def post(self, request):
        email = request.data.get('email')
        title = request.data.get('title')
        content = request.data.get('content')
        external_id = request.data.get('external_id')
        items_data = request.data.get('items', [])

        student, _ = Student.objects.get_or_create(email=email)

        questionnaire, _ = Questionnaire.objects.get_or_create(
            external_id=external_id,
            defaults={
                'content': content,
                'title': title,
            }
        )
        questionnaire.students.add(student)

        answers = []

        for item_data in items_data:
            item, _ = Item.objects.get_or_create(
                questionnaire=questionnaire,
                question=item_data.get('question'),
                defaults={
                    'subcontent': item_data.get('subcontent'),
                    'correct_answer': item_data.get('correct_answer')
                }
            )

            answer, _ = Answer.objects.get_or_create(
                item=item,
                text=item_data.get('answer'),
            )
            answer.students.add(student)
            answers.append(answer)

        try:
            feedbacks, correct_count_answers = check_answers(answers)
            formative_feedback = generate_formative_feedback(feedbacks, content)
        except Exception as e:
            return Response({'error_message': 'Error generating feedback', 'reason': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            send_feedback_email.delay(email, questionnaire.title, formative_feedback, correct_count_answers)
        except Exception as e:
            return Response({'error_message': 'Error sending email', 'reason': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Questionnaire submitted successfully'}, status=status.HTTP_201_CREATED)