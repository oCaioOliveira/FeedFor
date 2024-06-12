from django.db import models
import uuid


class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)

    class Meta:
        verbose_name_plural = "Alunos"

    def __str__(self):
        return self.email


class Questionnaire(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    content = models.CharField(max_length=255, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    external_id = models.CharField(max_length=255, blank=True, null=True, unique=True)

    student = models.ForeignKey(Student, related_name='questionnaires', on_delete=models.RESTRICT)

    class Meta:
        verbose_name_plural = "Questionarios"

    def __str__(self):
        return f"{self.id} - {self.name}"


class Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=255, blank=False, null=False)
    answer = models.CharField(max_length=255, blank=False, null=False)
    subcontent = models.CharField(max_length=255, blank=False, null=False)
    correct_answer = models.CharField(max_length=255, blank=False, null=False)

    questionnaire = models.ForeignKey(Questionnaire, related_name='items', on_delete=models.RESTRICT)

    class Meta:
        verbose_name_plural = "Itens"

    def __str__(self):
        return f"{self.id} - {self.question}"

