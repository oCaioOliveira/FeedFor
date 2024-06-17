from django.contrib import admin
from core.models import (
    Student,
    Questionnaire,
    Item,
    Answer,
    Result,
    ModelSettings,
    Teacher,
    Subject,
)


def truncate_text(text, max_length=40):
    if text and len(text) > max_length:
        return text[:max_length] + "..."
    return text


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "created_at")
    search_fields = ("name", "email")
    list_filter = ("created_at",)


@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "content", "external_id", "subject", "created_at")
    search_fields = ("title", "external_id")
    list_filter = ("created_at",)
    filter_horizontal = ("students",)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "get_truncated_question",
        "subcontent",
        "get_truncated_correct_answer",
        "created_at",
        "questionnaire",
    )
    search_fields = ("question", "subcontent", "correct_answer")
    list_filter = ("created_at", "questionnaire")

    def get_truncated_question(self, obj):
        return truncate_text(obj.question, max_length=40)

    get_truncated_question.short_description = "Question"

    def get_truncated_correct_answer(self, obj):
        return truncate_text(obj.question, max_length=40)

    get_truncated_correct_answer.short_description = "Correct Answer"


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "get_truncated_text",
        "correct",
        "get_truncated_feedback_explanation",
        "get_truncated_feedback_improve_suggestions",
        "item",
        "created_at",
    )
    search_fields = ("text", "feedback_explanation", "feedback_improve_suggestions")
    list_filter = ("created_at", "item")
    filter_horizontal = ("students",)

    def get_truncated_text(self, obj):
        return truncate_text(obj.text, max_length=40)

    get_truncated_text.short_description = "Text"

    def get_truncated_feedback_explanation(self, obj):
        return truncate_text(obj.feedback_explanation, max_length=40)

    get_truncated_feedback_explanation.short_description = "Feedback Explanation"

    def get_truncated_feedback_improve_suggestions(self, obj):
        return truncate_text(obj.feedback_improve_suggestions, max_length=40)

    get_truncated_feedback_improve_suggestions.short_description = (
        "Feedback Improve Suggestions"
    )


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("id", "score", "created_at", "student", "questionnaire")
    search_fields = ("id", "score", "student", "questionnaire")
    list_filter = ("created_at", "score")


@admin.register(ModelSettings)
class ModelSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "openai_api_key",
        "model",
        "get_truncated_system_content",
        "max_tokens",
        "temperature",
        "created_at",
    )
    search_fields = (
        "id",
        "openai_api_key",
        "model",
        "system_content",
        "max_tokens",
        "temperature",
    )
    list_filter = ("created_at",)

    def get_truncated_system_content(self, obj):
        return truncate_text(obj.system_content, max_length=40)

    get_truncated_system_content.short_description = "System Content"


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "created_at")
    search_fields = ("id", "name", "email")
    list_filter = ("created_at",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "model_settings", "created_at")
    search_fields = ("id", "name", "email")
    list_filter = ("created_at",)
    filter_horizontal = (
        "students",
        "teachers",
    )
