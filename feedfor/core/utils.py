def check_answers(answers: list) -> tuple:
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
