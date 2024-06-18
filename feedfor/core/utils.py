from .models import Answer


def check_answers(answers: list) -> tuple:
    feedbacks = []
    correct_count_answers = 0

    for answer in answers:
        correct_answers = (
            answer.item.correct_answer
            if type(answer.item.correct_answer) == list
            else [answer.item.correct_answer]
        )
        student_answers = answer.text if type(answer.text) == list else [answer.text]

        total_correct = len(correct_answers)
        is_correct = True
        wrong_answers = []
        result = {}
        number_of_correct_student_answers = 0

        for student_answer in student_answers:
            if student_answer in correct_answers:
                result[student_answer] = True
                number_of_correct_student_answers += 1
            else:
                result[student_answer] = False
                wrong_answers.append(student_answer)
                number_of_correct_student_answers -= 1
                is_correct = False

        score = max(number_of_correct_student_answers / total_correct, 0)

        if is_correct:
            correct_count_answers += 1

        feedback = {
            "question": answer.item.question,
            "answer": student_answers,
            "correct_answer": correct_answers,
            "correct": is_correct,
            "subcontent": answer.item.subcontent,
            "explanation": answer.feedback_explanation,
            "improve_suggestions": answer.feedback_improve_suggestions,
            "answer_id": answer.id,
            "wrong_answers": wrong_answers,
            "result": result,
            "score": score,
        }
        feedbacks.append(feedback)

        save_correct_answer(answer.id, score)

    return feedbacks, correct_count_answers


def save_correct_answer(answer_id: int, score: float) -> None:
    answer = Answer.objects.get(id=answer_id)
    answer.correct = score
    answer.save()
