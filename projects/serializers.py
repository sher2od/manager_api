from rest_framework import serializers
from django.utils import timezone
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    manager_name = serializers.ReadOnlyField(source='manager.username')

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description',
            'manager', 'manager_name',
            'start_date', 'end_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'manager', 'start_date', 'created_at', 'updated_at']

    def validate(self, attrs):
        end_date = attrs.get('end_date')
        if end_date and end_date < timezone.now().date():
            raise serializers.ValidationError({'end_date': "Tugash sanasi o'tib ketgan sana bo'lishi mumkin emas."})
        return attrs


