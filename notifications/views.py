from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Notification
from .serializers import NotificationSerializer


@extend_schema(tags=['Notifications'])
class NotificationViewSet(viewsets.ModelViewSet):
    """
    Foydalanuvchi bildirishnomalari uchun ViewSet.
    Faqat tizimga kirgan foydalanuvchiga tegishli bildirishnomalarni ko'rsatadi.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()

        user = self.request.user
        if user.role == 'admin':
            return Notification.objects.all().order_by('-created_at')

        return Notification.objects.filter(user=user).order_by('-created_at')

    def perform_create(self, serializer):
        if 'user' not in serializer.validated_data:
            serializer.save(user=self.request.user)
        else:
            serializer.save()

    @extend_schema(
        request=None,
        responses={200: OpenApiResponse(description="Bildirishnoma o'qilgan deb belgilandi")}
    )
    @action(detail=True, methods=['post'], url_path='mark-as-read')
    def mark_as_read(self, request, pk=None):
        """Alohida bitta bildirishnomani o'qilgan deb belgilash"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response(
            {"detail": "Bildirishnoma o'qilgan deb belgilandi."},
            status=status.HTTP_200_OK
        )

    @extend_schema(
        request=None,
        responses={200: OpenApiResponse(description="Barcha bildirishnomalar o'qilgan deb belgilandi")}
    )
    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        """Foydalanuvchining barcha bildirishnomalarini o'qilgan deb belgilash"""
        notifications = self.get_queryset().filter(is_read=False)
        updated_count = notifications.update(is_read=True)
        return Response(
            {"detail": f"{updated_count} ta bildirishnoma o'qilgan deb belgilandi."},
            status=status.HTTP_200_OK
        )
