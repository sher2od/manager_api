from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'user_username',
            'title', 'message', 'notification_type',
            'is_read', 'created_at'
        ]
        read_only_fields = [
            'id', 'user', 'title', 'message',
            'notification_type', 'created_at'
        ]

