from rest_framework import serializers


class ItemSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=1024)
    answer = serializers.JSONField()
    subcontent = serializers.CharField(max_length=1024)
    correct_answer = serializers.JSONField()

    def validate_answer(self, value):
        return self._validate_string_or_list(value, "answer")

    def validate_correct_answer(self, value):
        return self._validate_string_or_list(value, "correct_answer")

    def _validate_string_or_list(self, value, field_name):
        if isinstance(value, str):
            return [value]
        elif isinstance(value, list) and all(isinstance(item, str) for item in value):
            return value
        else:
            raise serializers.ValidationError(
                f"{field_name} must be a string or a list of strings."
            )


class SendFeedbackSerializer(serializers.Serializer):
    questionnaire_title = serializers.CharField(max_length=255)
    questionnaire_content = serializers.CharField(max_length=1024)
    questionnaire_external_id = serializers.CharField(max_length=255)
    student_email = serializers.EmailField()
    subject_code = serializers.CharField(max_length=255)
    subject_name = serializers.CharField(max_length=255, required=False)
    teacher_email = serializers.EmailField()
    assistant_id = serializers.CharField(max_length=255)
    items = ItemSerializer(many=True)


class ResendFeedbackSerializer(serializers.Serializer):
    student_emails = serializers.ListField(child=serializers.CharField(max_length=1024))
    questionnaire_external_id = serializers.CharField(max_length=255)
    feedback_recipient = serializers.JSONField()

    def validate_feedback_recipient(self, value):
        return self._validate_string_or_list(value, "feedback_recipient")

    def _validate_string_or_list(self, value, field_name):
        if isinstance(value, str):
            return [value]
        elif isinstance(value, list) and all(isinstance(item, str) for item in value):
            return value
        else:
            raise serializers.ValidationError(
                f"{field_name} must be a string or a list of strings."
            )


class SendReportSerializer(serializers.Serializer):
    questionnaire_external_id = serializers.CharField(max_length=255)
