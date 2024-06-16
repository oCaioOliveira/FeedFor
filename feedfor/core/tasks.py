from typing import List, Dict, Union
from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import Answer, ModelSettings
import openai
import os


@shared_task
def send_formative_feedback_email(
    email: str,
    questionnaire_title: str,
    feedbacks: List[Dict[str, Union[str, bool, int]]],
    correct_count_answers: int,
) -> None:
    try:
        html_string = render_to_string(
            "feedback_template.html",
            {
                "questionnaire_title": questionnaire_title,
                "feedbacks": feedbacks,
                "correct_count_answers": correct_count_answers,
            },
        )
        html = HTML(string=html_string)
        pdf_file = html.write_pdf()

        email_message = EmailMessage(
            f"Feedback Formativo - {questionnaire_title}",
            f'Olá, encontre em anexo o seu feedback formativo referente ao questionário: "{questionnaire_title}".',
            os.getenv("EMAIL_HOST_USER", ""),
            [email],
        )
        email_message.attach("formative_feedback.pdf", pdf_file, "application/pdf")
        email_message.send()

    except Exception as e:
        print(f"Error sending feedback email: {str(e)}")


@shared_task
def generate_formative_feedback(
    feedbacks: List[Dict[str, Union[str, bool, int]]],
    questionnaire_content: str,
    email: str,
    questionnaire_title: str,
    correct_count_answers: int,
    model_settings_id: str,
) -> None:
    try:
        model_settings = ModelSettings.objects.get(id=model_settings_id)
        detailed_feedbacks = generate_feedback_details(
            feedbacks, questionnaire_content, model_settings
        )

        send_formative_feedback_email.delay(
            email,
            questionnaire_title,
            detailed_feedbacks,
            correct_count_answers,
        )

    except Exception as e:
        print(f"Error generating formative feedback: {str(e)}")


def generate_feedback_details(
    feedbacks: List[Dict[str, Union[str, bool, int]]],
    questionnaire_content: str,
    model_settings: ModelSettings,
) -> List[Dict[str, Union[str, bool, int]]]:
    detailed_feedbacks = []

    for feedback in feedbacks:
        if feedback["correct"]:
            feedback_text = "Bom trabalho! Você acertou a questão."
        elif not (feedback["explanation"] and feedback["improve_suggestions"]):
            feedback_text = generate_openai_feedback(
                feedback, questionnaire_content, model_settings
            )

            (
                feedback["explanation"],
                feedback["improve_suggestions"],
            ) = format_feedback(feedback_text)

            save_feedback_to_answer(
                feedback["answer_id"],
                feedback["explanation"],
                feedback["improve_suggestions"],
            )

        detailed_feedbacks.append(feedback)

    return detailed_feedbacks


def format_feedback(
    feedback_text: str,
) -> Dict[str, str]:
    if (
        "Explicação" in feedback_text
        and "Sugestões de Aperfeiçoamento" in feedback_text
    ):
        explanation = (
            feedback_text.split("Explicação:")[1]
            .split("Sugestões de Aperfeiçoamento:")[0]
            .strip()
        )
        suggestions = feedback_text.split("Sugestões de Aperfeiçoamento:")[1].strip()
    else:
        explanation = feedback_text
        suggestions = ""

    return explanation, suggestions


def generate_openai_feedback(
    feedback: Dict[str, Union[str, bool, int]],
    questionnaire_content: str,
    model_settings: ModelSettings,
) -> str:
    max_tokens = model_settings.max_tokens
    prompt = (
        f"Questão: {feedback['question']}\n"
        f"Resposta do aluno: {feedback['answer']}\n"
        f"Resposta correta: {feedback['correct_answer']}\n"
        f"Conteúdo do questionário: {questionnaire_content}\n"
        f"Subconteúdo da questão: {feedback['subcontent']}\n"
        "Explique por que a resposta do aluno está incorreta e qual deveria ser a resposta certa.\n"
        "Além disso, sugira o que o aluno pode estudar para melhorar nesse assunto.\n"
        "Divida sua resposta em duas seções: 'Explicação:' e 'Sugestões de Aperfeiçoamento:'.\n"
        "Responda em texto simples, sem usar qualquer formatação como negrito, itálico ou sublinhado.\n"
        f"Limite sua resposta a {(max_tokens - 50) if max_tokens > 100 else max_tokens} tokens, responda sem exceder esse limite."
    )

    openai.api_key = model_settings.openai_api_key

    response = openai.ChatCompletion.create(
        model=model_settings.model,
        messages=[
            {
                "role": "system",
                "content": model_settings.system_content,
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        temperature=float(model_settings.temperature),
    )

    return response.choices[0].message["content"].strip()


def save_feedback_to_answer(
    answer_id: int, feedback_explanation: str, feedback_improve_suggestions: str
) -> None:
    answer = Answer.objects.get(id=answer_id)
    answer.feedback_explanation = feedback_explanation
    answer.feedback_improve_suggestions = feedback_improve_suggestions
    answer.save()
