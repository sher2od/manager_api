from rest_framework import viewsets, permissions, filters
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from .models import Task
from .serializers import TaskSerializer


@extend_schema(tags=['Tasks'])
class TaskViewSet(viewsets.ModelViewSet):
    """
    Vazifalar (Tasks) uchun ViewSet:
    - Admin: barcha vazifalarni ko'radi va boshqaradi.
    - Manager: faqat o'z loyihalaridagi yoki o'zi yaratgan vazifalarni ko'radi va yaratadi.
    - Employee: faqat o'ziga biriktirilgan (assigned) vazifalarni ko'radi.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'status', 'priority', 'assignee']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'deadline', 'priority']

    def get_queryset(self):
        # Swagger schema yaratish uchun
        if getattr(self, 'swagger_fake_view', False):
            return Task.objects.none()

        user = self.request.user

        # 1. Admin barcha vazifalarni ko'radi
        if user.role == 'admin' or user.is_superuser:
            return Task.objects.all()

        # 2. Manager o'z loyihalaridagi yoki o'zi yaratgan vazifalarni ko'radi
        if user.role == 'manager':
            return Task.objects.filter(
                project__manager=user
            ) | Task.objects.filter(
                creator=user
            )

        # 3. Employee faqat o'ziga biriktirilgan vazifalarni ko'radi (IDOR himoyasi)
        return Task.objects.filter(assignee=user)

    def perform_create(self, serializer):
        user = self.request.user
        # Faqat Admin va Manager yangi vazifa yarata oladi
        if user.role not in ['admin', 'manager'] and not user.is_superuser:
            raise PermissionDenied("Faqat Manager va Admin vazifa yarata oladi.")
        
        serializer.save(creator=user)



