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

        is_correct = True
        wrong_answers = []
        result = {}

        for student_answer in student_answers:
            result[student_answer] = True
            if not student_answer in correct_answers:
                result[student_answer] = False
                wrong_answers.append(student_answer)
                is_correct = False

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
        }
        feedbacks.append(feedback)

    return feedbacks, correct_count_answers
