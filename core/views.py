from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from .models import (
    Student,
    Questionnaire,
    Item,
    Answer,
    Result,
    Teacher,
    Subject,
    ChatSettings,
)
from typing import List, Dict, Union
from .tasks import generate_formative_feedback, send_email_with_report
from .exceptions import FeedbackGenerationException
from .utils import check_answers
from .serializers import (
    SendFeedbackSerializer,
    ResendFeedbackSerializer,
    SendReportSerializer,
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import pandas as pd
import io


class SendFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Submeter um questionário preenchido e gerar seu feedback",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "questionnaire_title": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Título do questionário"
                ),
                "questionnaire_content": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Conteúdo do questionário"
                ),
                "questionnaire_external_id": openapi.Schema(
                    type=openapi.TYPE_STRING, description="ID externo do questionário"
                ),
                "student_email": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Email do estudante"
                ),
                "subject_code": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Código da disciplina"
                ),
                "subject_name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Nome da disciplina"
                ),
                "teacher_email": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Email do professor"
                ),
                "chat_id": openapi.Schema(
                    type=openapi.TYPE_STRING, description="ID do chat"
                ),
                "items": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "question": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="Questão do questionário",
                            ),
                            "answer": openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Items(type=openapi.TYPE_STRING),
                                description="Respostas fornecidas pelo estudante",
                            ),
                            "subcontent": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="Subconteúdo da questão",
                            ),
                            "correct_answer": openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Items(type=openapi.TYPE_STRING),
                                description="Respostas corretas para a questão",
                            ),
                        },
                        required=["question", "answer", "subcontent", "correct_answer"],
                    ),
                    description="Itens do questionário",
                ),
            },
            required=[
                "questionnaire_title",
                "questionnaire_content",
                "questionnaire_external_id",
                "student_email",
                "subject_code",
                "subject_name",
                "teacher_email",
                "chat_id",
                "items",
            ],
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                "Questionário submetido com sucesso"
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response("Requisição inválida"),
            status.HTTP_401_UNAUTHORIZED: openapi.Response("Não autorizado"),
        },
    )
    def post(self, request) -> Response:
        serializer = SendFeedbackSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            try:
                data = request.data
                student_email: str = data.get("student_email")
                teacher_email: str = data.get("teacher_email")
                title: str = data.get("questionnaire_title")
                content: str = data.get("questionnaire_content")
                external_id: str = data.get("questionnaire_external_id")
                items_data: list = data.get("items", [])
                subject_name: str = data.get("subject_name")
                subject_code: str = data.get("subject_code")
                chat_id: str = data.get("chat_id")

                student, _ = Student.objects.get_or_create(email=student_email)
                teacher, _ = Teacher.objects.get_or_create(email=teacher_email)

                chat_settings = ChatSettings.objects.get(id=chat_id)

                subject = self._save_subject(
                    subject_code, subject_name, chat_settings, student, teacher
                )

                questionnaire, _ = Questionnaire.objects.get_or_create(
                    external_id=external_id,
                    defaults={
                        "content": content,
                        "title": title,
                        "subject": subject,
                    },
                )
                questionnaire.students.add(student)

                answers = self._save_items_and_answers(
                    questionnaire, items_data, student
                )

                self._process_feedback(
                    answers,
                    content,
                    student_email,
                    questionnaire,
                    student,
                    chat_settings,
                )

                return Response(
                    {
                        "message": "Questionnaire submitted successfully, sending feedback."
                    },
                    status=status.HTTP_201_CREATED,
                )

            except ObjectDoesNotExist as e:
                return self._handle_error("Object does not exist.", str(e))
            except Exception as e:
                return self._handle_error("Error processing request.", str(e))
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _save_subject(
        self,
        subject_code: str,
        subject_name: str,
        chat_settings: ChatSettings,
        student: Student,
        teacher: Teacher,
    ) -> Subject:
        default_attributes = {}

        if subject_name:
            default_attributes["name"] = subject_name
        default_attributes["chat_settings"] = chat_settings

        subject, _ = Subject.objects.get_or_create(
            code=subject_code,
            defaults=default_attributes,
        )

        subject.students.add(student)
        subject.teachers.add(teacher)
        subject.save()

        return subject

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

            answer_text = item_data.get("answer")
            try:
                if answer_text.startswith("[") and answer_text.endswith("]"):
                    answer_text = answer_text[2:-2]
                    answer_text = answer_text.replace("\\", "")
                    answer_text = answer_text.replace('\\"', '"')
                    answer_text = answer_text.split('","')
            except Exception:
                pass

            answer, _ = Answer.objects.get_or_create(
                item=item,
                text=answer_text,
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
        chat_settings: ChatSettings,
    ) -> None:
        try:
            feedbacks, correct_count_answers = check_answers(answers)
            self._save_result(feedbacks, questionnaire, student)
            generate_formative_feedback.delay(
                feedbacks,
                content,
                [email],
                questionnaire.title,
                correct_count_answers,
                chat_settings.id,
                email,
            )
        except Exception as e:
            raise FeedbackGenerationException("Error generating feedback", str(e))

    def _save_result(
        self,
        feedbacks: List[Dict[str, Union[str, bool, int]]],
        questionnaire: Questionnaire,
        student: Student,
    ) -> None:
        total_score = 0
        total_questions = 0
        for feedback in feedbacks:
            total_score += feedback["score"]
            total_questions += 1
        score = (total_score) * 100 / total_questions
        Result.objects.create(score=score, questionnaire=questionnaire, student=student)

    def _handle_error(self, message: str, reason: str) -> Response:
        return Response(
            {"error_message": message, "reason": reason},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ResendFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Reenviar um Feedback já criado",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "student_emails": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description="Lista de emails dos estudantes",
                ),
                "questionnaire_external_id": openapi.Schema(
                    type=openapi.TYPE_STRING, description="ID externo do questionário"
                ),
                "feedback_recipient": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Destinatário do feedback"
                ),
            },
            required=[
                "student_emails",
                "questionnaire_external_id",
                "feedback_recipient",
            ],
        ),
        responses={
            status.HTTP_200_OK: openapi.Response("Resending feedback"),
            status.HTTP_400_BAD_REQUEST: openapi.Response("Requisição inválida"),
            status.HTTP_401_UNAUTHORIZED: openapi.Response("Não autorizado"),
        },
    )
    def post(self, request) -> Response:
        serializer = ResendFeedbackSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            try:
                data = request.data
                student_emails: List[str] = data.get("student_emails")
                questionnaire_external_id: str = data.get("questionnaire_external_id")
                feedback_recipient: Union[str, List[str]] = data.get(
                    "feedback_recipient"
                )

                questionnaire = Questionnaire.objects.get(
                    external_id=questionnaire_external_id
                )

                recipient_emails = self._set_list_recipient_emails(
                    student_emails, questionnaire, feedback_recipient
                )

                self._build_feedback_context(
                    student_emails, questionnaire, recipient_emails
                )

                return Response(
                    {
                        "message": "Resending feedback.",
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return self._handle_error("Error recreating feedback.", str(e))
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _set_list_recipient_emails(
        self,
        student_emails: List[str],
        questionnaire: Questionnaire,
        feedback_recipient: Union[str, List[str]],
    ) -> Dict[str, List[str]]:
        recipient_emails = {}

        if feedback_recipient == "teachers" or feedback_recipient == "both":
            recipient_emails["teachers"] = list(
                questionnaire.subject.teachers.values_list("email", flat=True)
            )
        if feedback_recipient == "students" or feedback_recipient == "both":
            recipient_emails["students"] = student_emails
        if type(feedback_recipient) == list:
            recipient_emails["others"] = feedback_recipient

        return recipient_emails

    def _build_feedback_context(
        self,
        student_emails: List[str],
        questionnaire: Questionnaire,
        recipient_emails: Dict[str, List[str]],
    ):
        student_receive_email = len(recipient_emails.get("students", [])) > 0
        recipient_emails_without_student = recipient_emails.get(
            "teachers", []
        ) + recipient_emails.get("others", [])
        for student_email in student_emails:
            answers = list(
                Answer.objects.filter(
                    item__questionnaire__id=questionnaire.id,
                    students__email=student_email,
                )
            )
            if len(answers) > 0:
                feedbacks, correct_count_answers = check_answers(answers)
                generate_formative_feedback.delay(
                    feedbacks,
                    questionnaire.content,
                    (
                        recipient_emails_without_student + [student_email]
                        if student_receive_email
                        else recipient_emails_without_student
                    ),
                    questionnaire.title,
                    correct_count_answers,
                    questionnaire.subject.chat_settings.id,
                    student_email,
                )

    def _handle_error(self, message: str, reason: str) -> Response:
        return Response(
            {"error_message": message, "reason": reason},
            status=status.HTTP_400_BAD_REQUEST,
        )


class SendReportView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Solicitar um relatório de um questionário",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "questionnaire_external_id": openapi.Schema(
                    type=openapi.TYPE_STRING, description="ID externo do questionário"
                ),
            },
            required=[
                "questionnaire_external_id",
            ],
        ),
        responses={
            status.HTTP_200_OK: openapi.Response("Sending report"),
            status.HTTP_400_BAD_REQUEST: openapi.Response("Requisição inválida"),
            status.HTTP_401_UNAUTHORIZED: openapi.Response("Não autorizado"),
        },
    )
    def post(self, request) -> Response:
        serializer = SendReportSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            try:
                data = request.data
                questionnaire_external_id: str = data.get("questionnaire_external_id")

                questionnaire = Questionnaire.objects.get(
                    external_id=questionnaire_external_id
                )

                recipient_emails = list(
                    questionnaire.subject.teachers.values_list("email", flat=True)
                )

                report_file = self.generate_report(questionnaire)

                subject = f"Relatório do Questionário {questionnaire.title}"
                body = "Segue em anexo o relatório do questionário."

                send_email_with_report.delay(
                    subject, body, recipient_emails, report_file.getvalue()
                )

                return Response(
                    {
                        "message": "Sending report.",
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return self._handle_error("Error creating report.", str(e))
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def generate_report(self, questionnaire):
        students = questionnaire.students.all()
        items = questionnaire.items.all()
        results = Result.objects.filter(questionnaire=questionnaire)
        answers = Answer.objects.filter(item__questionnaire=questionnaire)

        data = []

        for student in students:
            student_data = {"Aluno": student.email}
            for item in items:
                student_answer = answers.filter(item=item, students=student).first()
                if student_answer:
                    student_data[item.question] = student_answer.correct
                else:
                    student_data[item.question] = 0.0

            student_results = (
                results.filter(student=student).order_by("-created_at").first()
            )
            student_score = student_results.score if student_results else 0
            student_data["Pontuação"] = student_score

            data.append(student_data)

        df = pd.DataFrame(data)

        question_stats_data = []
        for item in items:
            question = item.question
            correct_count = (df[question] == 1.0).sum()
            incorrect_count = (df[question] == 0.0).sum()
            parcial_correct_count = (
                df[question].between(0.0, 1.0, inclusive="neither").sum()
            )
            total_count = len(df)
            correct_percentage = (correct_count / total_count) * 100
            incorrect_percentage = (incorrect_count / total_count) * 100
            parcial_correct_percentage = (parcial_correct_count / total_count) * 100
            question_stats_data.append(
                {
                    "Questão": question,
                    "Corretas": correct_count,
                    "Parcialmente Corretas": parcial_correct_count,
                    "Incorretas": incorrect_count,
                    "Total": total_count,
                    "Corretas %": correct_percentage,
                    "Parcialmente Corretas %": parcial_correct_percentage,
                    "Incorretas %": incorrect_percentage,
                }
            )

        question_stats = pd.DataFrame(question_stats_data)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Desempenho dos Alunos")
            question_stats.to_excel(
                writer, index=False, sheet_name="Estatísticas das Questões"
            )

        output.seek(0)

        return output

    def _handle_error(self, message: str, reason: str) -> Response:
        return Response(
            {"error_message": message, "reason": reason},
            status=status.HTTP_400_BAD_REQUEST,
        )
