from rest_framework import serializers
from .models import Student, Questionnaire, Item


class ItemSerializer(serializers.ModelSerializer):
    questionnaire = serializers.PrimaryKeyRelatedField(queryset=Questionnaire.objects.all())

    class Meta:
        model = Item
        fields = ['id', 'question', 'subcontent', 'correct_answer', 'created_at', 'questionnaire']



class QuestionnaireSerializer(serializers.ModelSerializer):
    students = serializers.PrimaryKeyRelatedField(many=True, queryset=Student.objects.all())

    class Meta:
        model = Questionnaire
        fields = ['id', 'content', 'created_at', 'external_id', 'students']


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'email', 'created_at']


class AnswerSerializer(serializers.ModelSerializer):
    students = serializers.PrimaryKeyRelatedField(many=True, queryset=Student.objects.all())
    item = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all())

    class Meta:
        model = Answer
        fields = ['id', 'text', 'feedback', 'created_at', 'students', 'item']