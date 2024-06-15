from django.db import models
import uuid


class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Questionnaire(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, blank=False, null=False)
    content = models.CharField(max_length=255, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    external_id = models.CharField(max_length=255, blank=True, null=True, unique=True)

    students = models.ManyToManyField(Student, related_name='questionnaires')

    def __str__(self):
        return f"{self.id}"


class Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.TextField(blank=False, null=False)
    subcontent = models.CharField(max_length=255, blank=False, null=False)
    correct_answer = models.CharField(max_length=255, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    questionnaire = models.ForeignKey(Questionnaire, related_name='items', on_delete=models.RESTRICT)

    def __str__(self):
        return f"{self.id}"


class Answer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField(blank=False, null=False)
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    students = models.ManyToManyField(Student, related_name='answers')
    item = models.ForeignKey(Item, related_name='answers', on_delete=models.RESTRICT)

    def __str__(self):
        return f"{self.id}"