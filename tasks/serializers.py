from rest_framework import serializers
from django.utils import timezone
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    creator_username = serializers.ReadOnlyField(source='creator.username')
    assignee_username = serializers.ReadOnlyField(source='assignee.username')
    project_title = serializers.ReadOnlyField(source='project.title')

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description',
            'project', 'project_title',
            'creator', 'creator_username',
            'assignee', 'assignee_username',
            'status', 'priority', 'deadline',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'creator', 'created_at', 'updated_at']

    def validate_deadline(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Vazifa muddati o'tib ketgan vaqt bo'lishi mumkin emas.")
        return value