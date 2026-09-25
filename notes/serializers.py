from rest_framework import serializers
from .models import Note, Task


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = [
            "id", "title", "content",
            "ai_summary", "ai_tags", "ai_status",
            "created_at", "updated_at",
        ]
        read_only_fields = ["ai_summary", "ai_tags", "ai_status", "created_at", "updated_at"]


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "note", "title", "is_completed", "priority", "due_date", "created_at"]
        read_only_fields = ["created_at"]
