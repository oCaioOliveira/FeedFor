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


class AssistantSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    openai_api_key = models.CharField(max_length=255, blank=False, null=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    assistant_id = models.CharField(max_length=255, blank=True, null=True)
    model = models.CharField(max_length=255, blank=False, null=False)
    system_content_instructions = models.TextField(blank=False, null=False)
    max_completion_tokens = models.IntegerField(blank=False, null=False)
    temperature = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not (0.009 <= self.temperature <= 2.00):
            raise ValidationError(
                {"temperature": "Temperature must be between 0.01 and 2.00."}
            )


class Subject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=255, blank=False, null=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    assistant_settings = models.ForeignKey(
        AssistantSettings, related_name="subjects", on_delete=models.RESTRICT
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
        return f"{self.id}"


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
        return f"{self.id}"


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
        return f"{self.id}"


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
        return f"{self.id}"


@receiver(post_save, sender=AssistantSettings)
def create_or_update_assistant(sender, instance, created, **kwargs):
    try:
        client = OpenAI(api_key=instance.openai_api_key)

        if instance.assistant_id:
            assistant = client.beta.assistants.update(
                assistant_id=instance.assistant_id,
                name=instance.name,
                instructions=instance.system_content_instructions,
                temperature=float(instance.temperature),
                model=instance.model,
            )
        else:
            assistant = client.beta.assistants.create(
                name=instance.name,
                instructions=instance.system_content_instructions,
                temperature=float(instance.temperature),
                model=instance.model,
            )
            instance.assistant_id = assistant.id
            instance.save()
    except Exception as e:
        print(
            f"Failed to retrieve or create assistant {instance.assistant_id if instance.assistant_id else instance.name}: {str(e)}"
        )


@receiver(post_delete, sender=AssistantSettings)
def delete_assistant(sender, instance, **kwargs):
    try:
        client = OpenAI(api_key=instance.openai_api_key)

        client.beta.assistants.delete(assistant_id=instance.assistant_id)
    except Exception as e:
        print(f"Failed to delete assistant {instance.assistant_id}: {str(e)}")
