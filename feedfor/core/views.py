from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from .models import Student, Questionnaire, Item, Answer, Result
from .tasks import generate_formative_feedback
from .exceptions import FeedbackGenerationException


class SubmitQuestionnaireView(APIView):
    def post(self, request) -> Response:
        try:
            data = request.data
            email: str = data.get("email")
            title: str = data.get("title")
            content: str = data.get("content")
            external_id: str = data.get("external_id")
            items_data: list = data.get("items", [])

            student, _ = Student.objects.get_or_create(email=email)

            questionnaire, _ = Questionnaire.objects.get_or_create(
                external_id=external_id,
                defaults={
                    "content": content,
                    "title": title,
                },
            )
            questionnaire.students.add(student)

            answers = self._save_items_and_answers(questionnaire, items_data, student)

            self._process_feedback(answers, content, email, questionnaire, student)

            return Response(
                {"message": "Questionnaire submitted successfully"},
                status=status.HTTP_201_CREATED,
            )

        except ObjectDoesNotExist as e:
            return self._handle_error("Object does not exist", str(e))
        except Exception as e:
            return self._handle_error("Error processing request", str(e))

    def _save_items_and_answers(
        self, questionnaire: Questionnaire, items_data: list, student: Student
    ) -> list:
        answers: list = []
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

        return answers

    def _process_feedback(
        self,
        answers: list,
        content: str,
        email: str,
        questionnaire: Questionnaire,
        student: Student,
    ) -> None:
        try:
            openai_api_key: str = settings.OPENAI_API_KEY
            feedbacks, correct_count_answers = self._check_answers(answers)
            self._save_result(answers, correct_count_answers, questionnaire, student)
            generate_formative_feedback.delay(
                feedbacks,
                content,
                openai_api_key,
                email,
                questionnaire.title,
                correct_count_answers,
            )
        except Exception as e:
            raise FeedbackGenerationException("Error generating feedback", str(e))

    def _check_answers(self, answers: list) -> tuple:
        feedbacks = []
        correct_count_answers = 0

        for answer in answers:
            correct = answer.item.correct_answer
            student_answer = answer.text
            is_correct = correct.strip().lower() == student_answer.strip().lower()

            if is_correct:
                correct_count_answers += 1

            feedback = {
                "question": answer.item.question,
                "answer": student_answer,
                "correct_answer": correct,
                "correct": is_correct,
                "subcontent": answer.item.subcontent,
                "explanation": answer.feedback_explanation,
                "improve_suggestions": answer.feedback_improve_suggestions,
                "answer_id": answer.id,
            }
            feedbacks.append(feedback)

        return feedbacks, correct_count_answers

    def _save_result(
        self,
        answers: list,
        correct_count_answers: int,
        questionnaire: Questionnaire,
        student: Student,
    ) -> None:
        score = (correct_count_answers / len(answers)) * 100
        Result.objects.create(score=score, questionnaire=questionnaire, student=student)

    def _handle_error(self, message: str, reason: str) -> Response:
        return Response(
            {"error_message": message, "reason": reason},
            status=status.HTTP_400_BAD_REQUEST,
        )
