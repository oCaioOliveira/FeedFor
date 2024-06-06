from rest_framework import serializers
from .models import Student, Questionnaire, Item


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['question', 'answer', 'subject', 'correct_answer']


class QuestionnaireSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True)

    class Meta:
        model = Questionnaire
        fields = ['external_id', 'created_at', 'items']


class StudentSerializer(serializers.ModelSerializer):
    questionnaires = QuestionnaireSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = ['email', 'questionnaires']