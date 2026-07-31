from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Task

from .serializers import TaskSerializer
from users.permissions import IsManagerOrAdmin


@extend_schema(tags=['Tasks'])
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer


    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Task.objects.none()
        user = self.request.user
        if user.role in ['admin', 'manager']:
            return Task.objects.all()              
        return Task.objects.filter(assignee=user)  

    def perform_create(self, serializer):
        self.check_permissions_for_create()
        serializer.save(creator=self.request.user)

    def check_permissions_for_create(self):
        user = self.request.user
        if user.role not in ['admin', 'manager']:
            raise PermissionDenied("Faqat Manager va Admin task yarata oladi.")


