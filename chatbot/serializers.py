from rest_framework import serializers
from .models import Query, Question, Answer, Remedy

class QuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = ['id', 'text', 'is_pet_related', 'created_at', 'session_id']
        read_only_fields = ['is_pet_related', 'created_at']

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'order', 'created_at']
        read_only_fields = ['created_at']

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'question', 'text', 'created_at']
        read_only_fields = ['created_at']

class RemedySerializer(serializers.ModelSerializer):
    class Meta:
        model = Remedy
        fields = ['id', 'text', 'created_at']
        read_only_fields = ['created_at']

class QueryResponseSerializer(serializers.Serializer):
    query_id = serializers.IntegerField()
    next_question = QuestionSerializer(allow_null=True)
    remedy = serializers.CharField(allow_null=True)
    message = serializers.CharField(allow_null=True)


class SmartQuerySerializer(serializers.Serializer):
    query = serializers.CharField(
        required=False, 
        help_text="Your medical question about your pet (if you need to start a new session)"
    )
    answer = serializers.CharField(
        required=False, 
        help_text="Answer to the previous question (if continuing for previous question )"
    )