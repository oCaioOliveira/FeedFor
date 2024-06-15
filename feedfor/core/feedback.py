import openai
from django.conf import settings
from .models import Answer

openai.api_key = settings.OPENAI_API_KEY

def check_answers(answers):
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
            "feedback": answer.feedback,
            "answer_id": answer.id,
        }
        feedbacks.append(feedback)

    return feedbacks, correct_count_answers

def generate_formative_feedback(feedbacks, questionnaire_content):
    detailed_feedbacks = []

    for feedback in feedbacks:
        if feedback["correct"]:
            feedback_text = "Bom trabalho! Você acertou a questão."
        elif feedback["feedback"]:
            feedback_text = feedback["feedback"]
        else:
            prompt = (
                f"Questão: {feedback['question']}\n"
                f"Resposta do aluno: {feedback['answer']}\n"
                f"Resposta correta: {feedback['correct_answer']}\n"
                f"Conteúdo do questionário: {questionnaire_content}\n"
                f"Subconteúdo da questão: {feedback['subcontent']}\n"
                "Explique por que a resposta do aluno está incorreta e qual deveria ser a resposta certa.\n"
                "Além disso, relacione a explicação do erro com o conteúdo do questionário e subconteúdo da questão por meio da explicação."
            )

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um assistente útil."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )

            feedback_text = response.choices[0].message['content'].strip()

            answer = Answer.objects.get(id=feedback["answer_id"])
            answer.feedback = feedback_text
            answer.save()
        
        feedback["formative_feedback"] = feedback_text
        detailed_feedbacks.append(feedback)
    
    return detailed_feedbacks