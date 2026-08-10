from rest_framework import serializers
from django.utils import timezone
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    # Qo'shimcha tushunarli ko'rinish uchun read-only maydonlar
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
        # Xavfsizlik: creator va avto-sanalarni so'rov orqali o'zgartirib bo'lmaydi (Impersonation himoyasi)
        read_only_fields = ['id', 'creator', 'created_at', 'updated_at']

    def validate_deadline(self, value):
        # Mantiqiy tekshiruv: deadline o'tib ketgan vaqt bo'lishi mumkin emas
        if value and value < timezone.now():
            raise serializers.ValidationError("Vazifa muddati (deadline) o'tib ketgan vaqt bo'lishi mumkin emas.")
        return value