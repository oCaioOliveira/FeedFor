from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import models
from django.core.exceptions import ValidationError
from openai import OpenAI
import uuid


class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Teacher(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class ChatSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    openai_api_key = models.CharField(max_length=255, blank=False, null=False)
    principal_model = models.CharField(max_length=255, blank=False, null=False)
    special_model = models.CharField(max_length=255, blank=False, null=False)
    system_content_instructions = models.TextField(blank=False, null=False)
    max_tokens = models.IntegerField(blank=False, null=False)
    temperature = models.DecimalField(max_digits=5, decimal_places=2)
    top_p = models.DecimalField(max_digits=5, decimal_places=2)
    frequency_penalty = models.DecimalField(max_digits=5, decimal_places=2)
    presence_penalty = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not (0 <= self.temperature <= 2.00):
            raise ValidationError(
                {"temperature": "Temperature must be between 0.00 and 2.00."}
            )
        if not (0 <= self.top_p <= 1.00):
            raise ValidationError({"top_p": "Top P must be between 0.00 and 1.00."})
        if not (0 <= self.frequency_penalty <= 2.00):
            raise ValidationError(
                {
                    "frequency_penalty": "Frequency penalty must be between 0.00 and 2.00."
                }
            )
        if not (0 <= self.presence_penalty <= 2.00):
            raise ValidationError(
                {"presence_penalty": "Presence penalty must be between 0.00 and 2.00."}
            )

    def __str__(self):
        return f"{self.id}"


class Subject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=255, blank=False, null=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    chat_settings = models.ForeignKey(
        ChatSettings, related_name="subjects", on_delete=models.RESTRICT
    )
    students = models.ManyToManyField(Student, related_name="subjects")
    teachers = models.ManyToManyField(Teacher, related_name="subjects")

    def __str__(self):
        return f"{self.name} - {self.code}"


class Questionnaire(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, blank=False, null=False)
    content = models.CharField(max_length=255, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    external_id = models.CharField(max_length=255, blank=True, null=True, unique=True)

    subject = models.ForeignKey(
        Subject, related_name="questionnaires", on_delete=models.RESTRICT
    )
    students = models.ManyToManyField(Student, related_name="questionnaires")

    def __str__(self):
        return f"{self.title} - {self.external_id}"


class Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.TextField(blank=False, null=False)
    subcontent = models.CharField(max_length=255, blank=False, null=False)
    correct_answer = models.JSONField(blank=False, null=False, default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    questionnaire = models.ForeignKey(
        Questionnaire, related_name="items", on_delete=models.RESTRICT
    )

    def __str__(self):
        return f"{self.question[:20]}..."


class Answer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.JSONField(blank=False, null=False, default=list)
    feedback_explanation = models.TextField(blank=True, null=True)
    feedback_improve_suggestions = models.TextField(blank=True, null=True)
    correct = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    students = models.ManyToManyField(Student, related_name="answers")
    item = models.ForeignKey(Item, related_name="answers", on_delete=models.RESTRICT)

    def __str__(self):
        return f"{self.text[:20]}..."


class Result(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    student = models.ForeignKey(
        Student, related_name="results", on_delete=models.RESTRICT
    )
    questionnaire = models.ForeignKey(
        Questionnaire, related_name="results", on_delete=models.RESTRICT
    )

    def __str__(self):
        return f"{self.score}"
