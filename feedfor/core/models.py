from django.db import models
import uuid


class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)

    class Meta:
        verbose_name_plural = "Aluno"

    def __str__(self):
        return self.email
