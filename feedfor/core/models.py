from django.db import models
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


class ModelSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    openai_api_key = models.CharField(max_length=255, blank=False, null=False)
    model = models.CharField(max_length=255, blank=False, null=False)
    system_content = models.TextField(blank=False, null=False)
    max_tokens = models.IntegerField(blank=False, null=False)
    temperature = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


class Subject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=255, blank=False, null=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    model_settings = models.ForeignKey(
        ModelSettings, related_name="subjects", on_delete=models.RESTRICT
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
    correct_answer = models.TextField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    questionnaire = models.ForeignKey(
        Questionnaire, related_name="items", on_delete=models.RESTRICT
    )

    def __str__(self):
        return f"{self.id}"


class Answer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField(blank=False, null=False)
    feedback_explanation = models.TextField(blank=True, null=True)
    feedback_improve_suggestions = models.TextField(blank=True, null=True)
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
