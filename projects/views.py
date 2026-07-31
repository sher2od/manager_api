from rest_framework import viewsets
from .models import Project
from .serializers import ProjectSerializer
from users.permissions import IsManagerOrAdmin
from drf_spectacular.utils import extend_schema

@extend_schema(tags=['Projects'])
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsManagerOrAdmin]


    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)






