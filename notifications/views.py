from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Notification
from .serializers import NotificationSerializer
from .permissions import IsNotificationOwner


@extend_schema(tags=['Notifications'])
class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsNotificationOwner]
    http_method_names = ['get', 'patch', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()

        user = self.request.user
        if user.role == 'admin' or user.is_superuser:
            return Notification.objects.select_related('user').all()

        return Notification.objects.select_related('user').filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        request=None,
        responses={200: OpenApiResponse(description="Bildirishnoma o'qilgan deb belgilandi")}
    )
    @action(detail=True, methods=['post'], url_path='mark-as-read')
    def mark_as_read(self, request, pk=None):
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
        notifications = self.get_queryset().filter(is_read=False)
        updated_count = notifications.update(is_read=True)
        return Response(
            {"detail": f"{updated_count} ta bildirishnoma o'qilgan deb belgilandi."},
            status=status.HTTP_200_OK
        )

