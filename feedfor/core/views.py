from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import Student, Questionnaire, Item, Answer
from .utils import check_answers
from .tasks import send_feedback_email, generate_formative_feedback


class SubmitQuestionnaireView(APIView):
    def post(self, request):
        email = request.data.get("email")
        title = request.data.get("title")
        content = request.data.get("content")
        external_id = request.data.get("external_id")
        items_data = request.data.get("items", [])

        student, _ = Student.objects.get_or_create(email=email)

        questionnaire, _ = Questionnaire.objects.get_or_create(
            external_id=external_id,
            defaults={
                "content": content,
                "title": title,
            },
        )
        questionnaire.students.add(student)

        answers = []

        for item_data in items_data:
            item, _ = Item.objects.get_or_create(
                questionnaire=questionnaire,
                question=item_data.get("question"),
                defaults={
                    "subcontent": item_data.get("subcontent"),
                    "correct_answer": item_data.get("correct_answer"),
                },
            )

            answer, _ = Answer.objects.get_or_create(
                item=item,
                text=item_data.get("answer"),
            )
            answer.students.add(student)
            answers.append(answer)

        try:
            openai_api_key = settings.OPENAI_API_KEY
            feedbacks, correct_count_answers = check_answers(answers)
            generate_formative_feedback.delay(
                feedbacks,
                content,
                openai_api_key,
                email,
                questionnaire.title,
                correct_count_answers,
            )
        except Exception as e:
            return Response(
                {"error_message": "Error generating feedback", "reason": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Questionnaire submitted successfully"},
            status=status.HTTP_201_CREATED,
        )
