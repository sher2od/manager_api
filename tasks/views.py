from rest_framework import viewsets, permissions, filters
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from .models import Task
from .serializers import TaskSerializer


@extend_schema(tags=['Tasks'])
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'status', 'priority', 'assignee']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'deadline', 'priority']

    def get_queryset(self):
        
        if getattr(self, 'swagger_fake_view', False):
            return Task.objects.none()

        user = self.request.user


        if user.role == 'admin' or user.is_superuser:
            return Task.objects.all()

        if user.role == 'manager':
            return Task.objects.filter(
                project__manager=user
            ) | Task.objects.filter(
                creator=user
            )

        return Task.objects.filter(assignee=user)

    def perform_create(self, serializer):
        user = self.request.user
        
        if user.role not in ['admin', 'manager'] and not user.is_superuser:
            raise PermissionDenied("Faqat Manager va Admin vazifa yarata oladi.")
        
        serializer.save(creator=user)



