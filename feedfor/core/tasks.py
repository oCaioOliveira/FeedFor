from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from weasyprint import HTML

import os

@shared_task
def send_feedback_email(email, questionnaire_title, feedbacks, correct_count_answers):
    html_string = render_to_string('feedback_template.html', {'questionnaire_title': questionnaire_title, 'feedbacks': feedbacks, 'correct_count_answers': correct_count_answers})
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()

    email_message = EmailMessage(
        f'Feedback Formativo - {questionnaire_title}',
        f'Olá, encontre em anexo o seu feedback formativo referente ao questionário: "{questionnaire_title}".',
        os.getenv("EMAIL_HOST_USER", ""),
        [email]
    )
    email_message.attach('formative_feedback.pdf', pdf_file, 'application/pdf')
    email_message.send()