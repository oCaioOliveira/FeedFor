from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Student, Questionnaire, Item
from .serializers import StudentSerializer, QuestionnaireSerializer, ItemSerializer
from django.shortcuts import get_object_or_404

class SubmitQuestionnaireView(APIView):
    def post(self, request):
        email = request.data.get('email')
        external_id = request.data.get('external_id')
        items_data = request.data.get('items', [])

        student, _ = Student.objects.get_or_create(email=email)

        questionnaire = Questionnaire.objects.create(
            external_id=external_id,
            student=student
        )

        for item_data in items_data:
            Item.objects.create(
                questionnaire=questionnaire,
                question=item_data.get('question'),
                answer=item_data.get('answer'),
                subject=item_data.get('subject'),
                correct_answer=item_data.get('correct_answer')
            )

        return Response({'message': 'Questionnaire submitted successfully'}, status=status.HTTP_201_CREATED)