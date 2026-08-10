from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema
from .models import Project
from .serializers import ProjectSerializer
from users.permissions import IsManagerOrAdmin


@extend_schema(tags=['Projects'])
class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Project.objects.none()

        user = self.request.user
        if user.role == 'admin' or user.is_superuser:
            return Project.objects.all()

        return Project.objects.filter(manager=user)

    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)







