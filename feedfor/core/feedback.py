import openai
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY

def check_answers(items):
    feedbacks = []

    for item in items:
        correct = item.get("correct_answer")
        student_answer = item.get("answer")
        is_correct = correct.strip().lower() == student_answer.strip().lower()

        feedback = {
            "question": item.get("question"),
            "answer": student_answer,
            "correct_answer": correct,
            "correct": is_correct,
            "subcontent": item.get("subcontent"),
        }
        feedbacks.append(feedback)
    
    return feedbacks

def generate_formative_feedback(feedbacks, questionnaire_subject):
    detailed_feedbacks = []

    for feedback in feedbacks:
        if feedback["correct"]:
            feedback_text = "Bom trabalho! Você acertou a questão."
        else:
            prompt = (
                f"Questão: {feedback['question']}\n"
                f"Resposta do aluno: {feedback['answer']}\n"
                f"Resposta correta: {feedback['correct_answer']}\n"
                f"Assunto do questionário: {questionnaire_subject}\n"
                f"Subconteúdo: {feedback['subcontent']}\n"
                "Explique por que a resposta do aluno está incorreta e qual deveria ser a resposta correta. "
                "Relacione a explicação do erro com o conteúdo e subconteúdo."
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

            # MOCK_FEEDBACK
            # feedback_text = (
            #     f"A questão estava relacionada ao subconteúdo '{feedback['subcontent']}'. "
            #     f"A resposta correta é '{feedback['correct_answer']}'. "
            #     "Revise o conteúdo sobre este tópico para melhorar seu entendimento."
            # )
        
        feedback["formative_feedback"] = feedback_text
        detailed_feedbacks.append(feedback)
    
    return detailed_feedbacks